#include <Wire.h>
#include <BH1750.h>
#include <DHT.h>

// --- Pins ---
const int LED1 = 4;
const int LED2 = 6;

const int FAN_ENA = 5;       // ENA L298N -> vitesse ventilateur
const int FAN_IN1 = 7;       // IN1 L298N
const int FAN_IN2 = 8;       // IN2 L298N

const int HEATER_PIN = 9;    // chauffage
const int DHTPIN = 2;

#define DHTTYPE DHT22        // mets DHT11 si besoin

// --- Seuils ---
const float SEUIL_LUM = 20;
const float T_CHAUFFE = 10 ;
const float T_STOP_CHAUFFE = 20;

const float T_VENTILO_MIN = 23;
const float T_VENTILO_MAX = 30;

BH1750 lightMeter;
DHT dht(DHTPIN, DHTTYPE);

bool chauffageOn = false;

void setup() {

  Serial.begin(9600);

  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);

  pinMode(FAN_ENA, OUTPUT);
  pinMode(FAN_IN1, OUTPUT);
  pinMode(FAN_IN2, OUTPUT);

  pinMode(HEATER_PIN, OUTPUT);

  digitalWrite(LED1, LOW);
  digitalWrite(LED2, LOW);

  digitalWrite(FAN_IN1, LOW);
  digitalWrite(FAN_IN2, LOW);

  analogWrite(FAN_ENA, 0);

  

  Wire.begin();
  dht.begin();

  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("BH1750 OK");
  } else {
    Serial.println("BH1750 introuvable");
  }
}

void loop() {

  // ========== LUMIERE -> LED ==========

  float lux = lightMeter.readLightLevel();

  // Etat Eclairage
  bool eclairageOn;

  if (lux < SEUIL_LUM) {

    digitalWrite(LED1, HIGH);
    digitalWrite(LED2, HIGH);

    eclairageOn = true;

  } else {

    digitalWrite(LED1, LOW);
    digitalWrite(LED2, LOW);

    eclairageOn = false;
  }


  // ========== TEMPERATURE + HUMIDITE ==========

  float temp = dht.readTemperature();
  float hygro = dht.readHumidity();

  if (!isnan(temp) && !isnan(hygro)) {

    // ===== CHAUFFAGE =====

    if (temp < T_CHAUFFE) {
      chauffageOn = true;
      digitalWrite(HEATER_PIN,LOW);
  }

    if (temp >= T_STOP_CHAUFFE) {
      chauffageOn = false;
      digitalWrite(HEATER_PIN,HIGH);
    }


    // ===== VENTILATEUR =====

    int vitesseVentilo = 0;

    // Moins de 23°C -> 0%
    if (temp < 23) {

      vitesseVentilo = 0;

    }

    // 23°C à moins de 25°C -> environ 20%
    else if (temp >= 23 && temp < 25) {

      vitesseVentilo = 20;

    }

    // 25°C à moins de 27°C -> environ 31%
    else if (temp >= 25 && temp < 27) {

      vitesseVentilo = 30;

    }

    // 27°C à moins de 29°C -> environ 47%
    else if (temp >= 27 && temp < 29) {

      vitesseVentilo = 40;

    }

    // 29°C ou plus -> maximum 60%
    else {

      vitesseVentilo = 50;

    }


    // ===== SECURITE =====

    // Pas de chauffage quand le ventilateur fonctionne
    //if (vitesseVentilo > 0) {
    //  chauffageOn = false;
    //}


    // ===== COMMANDE VENTILATEUR =====

    if (vitesseVentilo > 0) {

      digitalWrite(FAN_IN1, HIGH);
      digitalWrite(FAN_IN2, LOW);

      analogWrite(FAN_ENA, vitesseVentilo);

    } else {

      digitalWrite(FAN_IN1, LOW);
      digitalWrite(FAN_IN2, LOW);

      analogWrite(FAN_ENA, 0);
    }


    // ===== CHAUFFAGE =====

   digitalWrite(
    HEATER_PIN,
      chauffageOn ? LOW : HIGH
    );


    // ==================================================
    // AFFICHAGE ORGANISE POUR LA BASE DE DONNEES
    // ==================================================

    // ----- GROUPE GAUCHE : readings -----

    Serial.print("temp = ");
    Serial.print(temp, 1);

    Serial.print(" ; ");

    Serial.print("hygro = ");
    Serial.print(hygro, 1);

    Serial.print(" ; ");

    Serial.print("lux = ");
    Serial.print(lux, 1);


    // ----- SEPARATION -----

    Serial.print(" | ");


    // ----- GROUPE DROITE : equipments -----

    Serial.print("Ventilateur = ");

    if (vitesseVentilo > 0) {
      Serial.print("ON");
    } else {
      Serial.print("OFF");
    }

    Serial.print(" ; ");

    Serial.print("Chauffage = ");
    Serial.print(chauffageOn ? "ON" : "OFF");

    Serial.print(" ; ");

    Serial.print("Eclairage = ");
    Serial.println(eclairageOn ? "ON" : "OFF");
  }


  // ========== ERREUR DHT ==========

  else {

    Serial.print("temp = ERROR ; ");

    Serial.print("hygro = ERROR ; ");

    Serial.print("lux = ");
    Serial.print(lux, 1);

    Serial.print(" | ");

    Serial.print("Ventilateur = ERROR");
    Serial.print(" ; ");

    Serial.print("Chauffage = ERROR");
    Serial.print(" ; ");

    Serial.println("Eclairage = ERROR");
  }

  delay(1000);
}