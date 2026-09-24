PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY,
    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP UNIQUE,
    temp REAL NOT NULL,
    hygro REAL NOT NULL,
    lux REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS equipements (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    equipement_id INTEGER NOT NULL,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    ended_at TEXT,
    FOREIGN KEY (equipement_id) REFERENCES equipements(id)
);
    
INSERT OR IGNORE INTO equipements (name) VALUES ('Ventilateur');
INSERT OR IGNORE INTO equipements (name) VALUES ('Chauffage');
INSERT OR IGNORE INTO equipements (name) VALUES ('Eclairage');
