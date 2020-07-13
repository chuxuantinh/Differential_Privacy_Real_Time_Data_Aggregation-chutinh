#include <SoftwareSerial.h>

SoftwareSerial mySerial(6, 7); // RX, TX

void setup() {
  Serial.begin(115200);
  while (!Serial);
  mySerial.begin(115200);
}

int values[5];

int readIntFromSerial(void) {
  String intStr = "";
  char readByte;
  do {
    readByte = mySerial.read();
    if ((int)readByte != -1) {
     intStr += String(readByte);
    }
  } while (readByte != '\n');
  return intStr.toInt();
}

void loop() {
  int i, j;
  for (j = 0; j < 2; j++) {
    Serial.println("Sending HRM req");
    mySerial.println("hrmReq");
    Serial.println("Sent HRM req");
    Serial.println("Begin reception");
    for (i = 0; i < 5; i++) {
      values[i] = readIntFromSerial();
    }
    for (i = 0; i < 5; i++) {
      Serial.println(values[i]);
    }
    Serial.println("End reception");
  }
  delay(500);
  exit(0);
}
