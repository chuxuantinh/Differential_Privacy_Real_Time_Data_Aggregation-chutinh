void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.println("Testing");
  Serial.println("Testing again");
  Serial.println("Testing once more");
  Serial.println("Finished testing successive printing");
  delay(500);
  exit(0);
}
