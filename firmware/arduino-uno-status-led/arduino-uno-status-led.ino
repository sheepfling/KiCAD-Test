// training fixture — NOT FOR MANUFACTURE.
// J1.1 connects to Arduino Uno R3 D13 / LED_BUILTIN; J1.2 is GND.

constexpr uint8_t STATUS_LED_PIN = LED_BUILTIN;

void setup() {
  pinMode(STATUS_LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(STATUS_LED_PIN, HIGH);
  delay(500);
  digitalWrite(STATUS_LED_PIN, LOW);
  delay(500);
}
