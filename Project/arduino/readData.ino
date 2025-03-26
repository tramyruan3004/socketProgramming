#include <DHT.h>
#define DHTPIN 2        
#define DHTTYPE DHT11   

#define FLOAT_SENSOR_PIN 4

int LEDG = 8;    // Green LED
int LEDY = 9;    // Yellow LED
int LEDR = 10;   // Red LED
const int soilMoisturePin = A1;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(9600);
    // Initialize digital pins as outputs
    pinMode(LEDG, OUTPUT);
    pinMode(LEDY, OUTPUT);
    pinMode(LEDR, OUTPUT);
    
    pinMode(FLOAT_SENSOR_PIN, INPUT_PULLUP);  // Use internal pull-up

    dht.begin();
}

void loop() {
    digitalWrite(LEDY, LOW);  // Turn LED OFF
    digitalWrite(LEDG, LOW);
    digitalWrite(LEDR, LOW);
    int soilSensorValue = analogRead(soilMoisturePin);
    Serial.print("Moisture: ");
    Serial.println(soilSensorValue);
  
    float h = dht.readHumidity();
    float t = dht.readTemperature(); // Celsius
    if (isnan(h) || isnan(t)) {
      Serial.println("Failed to read from DHT sensor!");
      return;
    }
    Serial.print("Humidity: ");
    Serial.print(h);
    Serial.print(" %  |  Temperature: ");
    Serial.print(t);
    Serial.println(" °C");
  
    int floatSensorValue = digitalRead(FLOAT_SENSOR_PIN);  // Read sensor state
    Serial.print("Water Level:");
    Serial.println(floatSensorValue);
    Serial.println("==================");
    
    if (floatSensorValue == 1 && t > 27.5 && h > 75.0 && soilSensorValue > 750 ) { 
        Serial.println("THROW UR STUFF!");
        digitalWrite(LEDR, HIGH);  // Turn LED ON
    } else if (floatSensorValue == 1 && t < 27.5 && h > 70.0 && soilSensorValue > 600) {
        Serial.println("ALERT: CAN SPEND SOME TIME TO CHECK UR STUFF");
        digitalWrite(LEDY, HIGH);   // Turn LED OFF
    }else{
        digitalWrite(LEDG, HIGH);  
    }
    delay(30000);
}
