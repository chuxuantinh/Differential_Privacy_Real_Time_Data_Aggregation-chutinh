#include <SoftwareSerial.h>

SoftwareSerial mySerial(6, 7); // RX, TX

void setup() {
  Serial.begin(9600);
  while (!Serial);
  mySerial.begin(9600);
}

float valuesOnGreen[5], valuesOnBlue[5];

float readFloatFromSerial(void) {
  String floatStr = "";
  char readByte;
  do {
    readByte = mySerial.read();
    if ((int)readByte != -1) {
     floatStr += String(readByte);
    }
  } while (readByte != '\n');
  return floatStr.toFloat();
}

void loop() {
  int i;
  randomSeed(analogRead(5));
  for (i = 0; i < 5; i++) {
    valuesOnBlue[i] = readFloatFromSerial();
  }
  for (i = 0; i < 5; i++) {
    valuesOnGreen[i] = random(0, 100) / 99.0;
    mySerial.println(valuesOnGreen[i]);
  }
  for (i = 0; i < 5; i++) {
    Serial.println(valuesOnGreen[i]);
  }
  for (i = 0; i < 5; i++) {
    Serial.println(valuesOnBlue[i]);
  }
  delay(500);
  exit(0);
}
