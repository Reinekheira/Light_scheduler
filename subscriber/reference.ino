const int relayPin = 2;  // Pin connected to relay

void setup() {
  Serial.begin(9600);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);  // Start with light off
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    if (command == '1') {
      digitalWrite(relayPin, HIGH);  // Turn light on
      Serial.println("Light ON");
    } else if (command == '0') {
      digitalWrite(relayPin, LOW);   // Turn light off
      Serial.println("Light OFF");
    }
  }
}