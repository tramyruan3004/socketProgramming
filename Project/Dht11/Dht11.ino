#include <DHT.h>

// Define sensor type and pin
#define DHTPIN 2        // Pin connected to the DATA pin
#define DHTTYPE DHT11   // DHT 11 Sensor

// Initialize DHT sensor
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Serial.println("DHT11 Sensor Reading...");
  dht.begin();
}

void loop() {
  delay(2000);  // Wait 2 seconds between readings

  float h = dht.readHumidity();
  float t = dht.readTemperature(); // Celsius

  // Check if reading is valid
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.print(" %  |  Temperature: ");
  Serial.print(t);
  Serial.println(" °C");
}
