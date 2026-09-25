# Workshop — Serre connectée

Un Arduino relève la température, l'humidité et la luminosité, et pilote le ventilateur, le chauffage et l'éclairage.
Il envoie ses mesures par port série à un Raspberry Pi 3, qui les enregistre dans une base SQLite et les affiche sur un tableau de bord web.

```text
Arduino ──(USB / série)──> collect.py ──> serre.db (SQLite) ──> data.php ──> index.php + script.js
```

## Arborescence

```text
WorkShop/
├── arduino/
│   └── codeOK_final.ino
├── impression3d/
│   ├── boitier yanis.stl
│   ├── couvercle yanis.stl
│   ├── helice yanis.stl
│   └── porte yanis.stl
├── raspberry/
│   ├── index.php
│   ├── data.php
│   ├── script.js
│   ├── style.css
│   ├── img/bg.jpg
│   ├── js/chart.umd.min.js
│   ├── db/
│   │   ├── schema.sql
│   │   └── serre.db
│   └── scripts/
│       └── collect.py
├── Dockerfile
└── docker-compose.yml
```

## Arduino

| Fichier | Rôle |
| --- | --- |
| `arduino/codeOK_final.ino` | Lit les capteurs (DHT22 pour la température et l'humidité, BH1750 pour la luminosité), active les équipements selon des seuils et envoie une ligne par mesure sur le port série à 9600 bauds. |

Chaque ligne contient les mesures et l'état des équipements, séparés par `|` :

```text
temp=22.5;hygro=60.0;lux=120.0|Ventilateur=OFF;Chauffage=OFF;Eclairage=ON
```

## Raspberry Pi

### Collecte

| Fichier | Rôle |
| --- | --- |
| `raspberry/scripts/collect.py` | Ouvre le port série (`/dev/ttyACM0`), attend 2 s que l'Arduino redémarre, ignore la première ligne puis lit les trames en continu. Enregistre les mesures dans `readings` et ouvre ou ferme un événement dans `events` à chaque changement d'état d'un équipement. |

### Base de données

| Fichier | Rôle |
| --- | --- |
| `raspberry/db/schema.sql` | Crée les tables et insère les trois équipements. |
| `raspberry/db/serre.db` | Base SQLite (ignorée par git). |

Tables :

- `readings` : une ligne par mesure (`temp`, `hygro`, `lux`, `recorded_at`).
- `equipements` : Ventilateur, Chauffage, Eclairage.
- `events` : périodes de fonctionnement d'un équipement (`started_at`, et `ended_at` qui reste vide tant que l'équipement est allumé).

Créer la base :

```bash
sqlite3 raspberry/db/serre.db < raspberry/db/schema.sql
```

### Tableau de bord web

| Fichier | Rôle |
| --- | --- |
| `raspberry/index.php` | Page principale : onglets température / humidité / luminosité, graphique et un voyant par équipement (généré depuis la table `equipements`). |
| `raspberry/data.php` | API JSON appelée par la page : dernière mesure, équipements actifs, 50 dernières mesures et statistiques par équipement (nombre de cycles, durée cumulée). |
| `raspberry/script.js` | Appelle `data.php` toutes les secondes, met à jour les valeurs, les voyants (classe `on`) et le graphique. |
| `raspberry/style.css` | Styles de la page. Un voyant est rouge par défaut et vert avec la classe `on`. |
| `raspberry/js/chart.umd.min.js` | Bibliothèque Chart.js, embarquée localement pour fonctionner sans internet. |
| `raspberry/img/bg.jpg` | Image de fond. |

## Impression 3D

| Dossier | Rôle |
| --- | --- |
| `impression3d/` | Modèles STL de la serre : boîtier, couvercle, hélice du ventilateur et porte. |

## Développement (Docker)

| Fichier | Rôle |
| --- | --- |
| `Dockerfile` | Image PHP 8.2 + Apache qui sert le dossier `raspberry/`. |
| `docker-compose.yml` | Lance le conteneur derrière Traefik, accessible sur `http://raspberry.test`. Le dossier `raspberry/` est monté en volume pour voir les modifications en direct. |

```bash
docker compose up -d --build
```

## Déploiement sur le Raspberry Pi

Le projet est développé dans le conteneur, puis copié sur le Raspberry Pi 3 par SSH.
Sur le Pi, il faut un serveur web avec PHP et l'extension SQLite3, ainsi que Python 3 avec `pyserial` pour `collect.py` :

```bash
python3 raspberry/scripts/collect.py
```
