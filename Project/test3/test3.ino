#define INPUT_PIN 7  // Define pin 2 as the input pin

void setup() {
  Serial.begin(9600);       // Start serial communication
  pinMode(INPUT_PIN, INPUT); // Set pin 2 as an input
}

void loop() {
  int pinState = digitalRead(INPUT_PIN); // Read pin 2 state

  // Check if the pin is HIGH or LOW
  if (pinState == HIGH) {
    Serial.println("🔴 Pin 2 is HIGH (ON)");
  } else {
    Serial.println("⚫ Pin 2 is LOW (OFF)");
  }

  delay(500); // Wait 500ms before reading again
}
