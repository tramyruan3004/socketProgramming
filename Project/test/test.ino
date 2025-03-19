int LEDG = 8;    // Green LED
int LEDY = 9;    // Yellow LED
int LEDR = 10;   // Red LED
const int soilMoisturePin = A1;
const int airValue = 620;    // Value when sensor is in air (dry)
const int waterValue = 310;  // Value when sensor is in water (wet)
#define Float_Switch 3       // Float sensor connected to pin 3

// Define thresholds for moisture levels
const int lowMoistureThreshold = 30;   // Below this is considered low moisture
const int highMoistureThreshold = 70;  // Above this is considered high moisture

void setup() {
  Serial.begin(9600);
  Serial.println("Cytron Gravity Analog Soil Moisture Sensor Test");
  Serial.println("------------------------------------------------");
  
  // Initialize digital pins as outputs
  pinMode(LEDG, OUTPUT);
  pinMode(LEDY, OUTPUT);
  pinMode(LEDR, OUTPUT);
 
  pinMode(Float_Switch, INPUT_PULLUP);
  
  delay(2000);
}

void loop() {
  // Read soil moisture sensor
  int sensorValue = analogRead(soilMoisturePin);
  Serial.print("Moisture: ");
  Serial.print(sensorValue);
//  int moisturePercentage = map(sensorValue, airValue, waterValue, 0, 100);
//  moisturePercentage = constrain(moisturePercentage, 0, 100);
  
  // Read float switch (water level)
  int waterLevel = digitalRead(Float_Switch);
  Serial.println("Water level: ");
  Serial.print(waterLevel);
  // Determine moisture level category
//  String moistureStatus;
//  if (moisturePercentage < lowMoistureThreshold) {
//    moistureStatus = "LOW";
//  } else if (moisturePercentage > highMoistureThreshold) {
//    moistureStatus = "HIGH";
//  } else {
//    moistureStatus = "MEDIUM";
//  }
  
  // Determine water level category
  // Note: Since you're using a float switch, it's either HIGH or LOW
  // You might need a different sensor for medium water level detection
  // For now, we'll treat LOW switch reading as LOW water and HIGH as HIGH water
//  String waterStatus = (waterLevel == LOW) ? "LOW" : "HIGH";
  
  // Print debug information
//  Serial.print("Moisture: ");
//  Serial.print(moisturePercentage);
//  Serial.print("% (");
//  Serial.print(moistureStatus);
//  Serial.print(") | Water Level: ");
//  Serial.println(waterStatus);
  
//  // Turn off all LEDs initially
//  digitalWrite(LEDG, LOW);
//  digitalWrite(LEDY, LOW);
//  digitalWrite(LEDR, LOW);
//  
//  // Control LEDs based on conditions
//  if (moistureStatus == "HIGH" && waterStatus == "HIGH") {
//    // High moisture and high water - RED
//    digitalWrite(LEDR, HIGH);
//    Serial.println("Status: HIGH MOISTURE & HIGH WATER - RED LED ON");
//  } 
//  else if (moistureStatus == "MEDIUM" && (waterStatus == "MEDIUM" || waterStatus == "HIGH")) {
//    // Medium moisture and medium water - YELLOW
//    // Note: since float switch is binary, we're accepting HIGH as "medium or high"
//    digitalWrite(LEDY, HIGH);
//    Serial.println("Status: MEDIUM CONDITIONS - YELLOW LED ON");
//  }
//  else if (moistureStatus == "LOW" && waterStatus == "LOW") {
//    // Low moisture and low water - GREEN
//    digitalWrite(LEDG, HIGH);
//    Serial.println("Status: LOW MOISTURE & LOW WATER - GREEN LED ON");
//  }
  
  // Wait for 1 second before the next reading
  delay(1000);
}
