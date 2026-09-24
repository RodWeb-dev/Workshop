# --- collect.py ---

import pathlib
import sqlite3

import serial

path = pathlib.Path(__file__).parent.parent.resolve()

timeout = 3  # Délai d'attente pour la lecture du port série
rate = 9600  # Vitesse de communication du port série
port = "/dev/pts/9"

db = sqlite3.connect(path / "db/serre.db")
db.execute("PRAGMA foreign_keys = ON")

print("db connected")

equipements = {}
db_equipements = db.execute("SELECT id, name FROM equipements").fetchall()
for equipement_id, name in db_equipements:
    equipements[name] = {"ID": equipement_id, "Etat": False, "Event_id": None}


# Insérer les données dans la table readings
def insert_real_data(data):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO readings (temp, hygro, lux) VALUES (?, ?, ?)",
        (data["temp"], data["hygro"], data["lux"]),
    )
    db.commit()


# Démarrer un événement dans la table events
def start_event(
    equipement_id,
):
    cursor = db.cursor()
    cursor.execute("INSERT INTO events (equipement_id) VALUES (?)", (equipement_id,))
    db.commit()
    return cursor.lastrowid


# Terminer un événement dans la table events
def end_event(
    event_id,
):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE events SET ended_at = CURRENT_TIMESTAMP WHERE id = ?",
        (event_id,),
    )
    db.commit()


# parser les les données réelles reçues depuis le port série
def parse_real(text):
    real = text.split("|")[0]
    data = {}
    real = real.split(";")
    for paire in real:
        cle, valeur = paire.split("=")
        data[cle] = float(valeur)
    return data


# détecter les changements d'état des équipements et déclencher un événement si nécessaire
def parse_binary(text):
    binary = text.split("|")[1]
    binary = binary.split(";")
    for paire in binary:
        cle, valeur = paire.split("=")
        if valeur == "ON" and not equipements[cle]["Etat"]:
            equipements[cle]["Etat"] = True
            equipements[cle]["Event_id"] = start_event(equipements[cle]["ID"])
        elif valeur == "OFF" and equipements[cle]["Etat"]:
            equipements[cle]["Etat"] = False
            end_event(equipements[cle]["Event_id"])
            equipements[cle]["Event_id"] = None


# Lires les données depuis le port série
with serial.Serial(port, rate, timeout=timeout) as ser:
    print("Serial port opened")
    while True:
        line = ser.readline()
        if line:
            print(f"Received: {line}")
            text = line.decode("utf-8", errors="ignore").strip()
            if text:
                print(f"Parsed: {text}")
                data = parse_real(text)
                insert_real_data(data)
                parse_binary(text)
