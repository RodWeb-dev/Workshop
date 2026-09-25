# --- collect.py ---

import pathlib
import sqlite3
import time

import serial

path = pathlib.Path(__file__).parent.parent.resolve()

timeout = 3  # Délai d'attente pour la lecture du port série
rate = 9600  # Vitesse de communication du port série
port = "/dev/ttyACM0"  # Port série à utiliser

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
        cle = cle.strip()
        valeur = valeur.strip()
        data[cle] = float(valeur)
    return data


# détecter les changements d'état des équipements et déclencher un événement si nécessaire
def parse_binary(text):
    binary = text.split("|")[1]
    binary = binary.split(";")
    for paire in binary:
        cle, valeur = paire.split("=")
        cle = cle.strip()
        valeur = valeur.strip()
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
    time.sleep(2)  # Attendre que le port série soit prêt
    reset = ser.reset_input_buffer()  # Réinitialiser le tampon d'entrée
    ser.readline()  # Lire la première ligne pour ignorer les données initiales
    while True:
        line = ser.readline()
        if line:
            print(f"Received: {line}")
            text = line.decode("utf-8", errors="ignore").strip()
            if text:
                try:
                    print(f"Parsed: {text}")
                    data = parse_real(text)
                    insert_real_data(data)
                    parse_binary(text)
                except (ValueError, KeyError, IndexError) as e:
                    print(f"Error parsing line: {e}")
                    print(f"Line content: {text}")
