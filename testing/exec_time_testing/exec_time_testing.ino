void setup() {
  Serial.begin(9600);
}

int t1, t2, t3;

void func1(void) {
  int i, temp;
  for (i = 0; i < 100; i++) {
    // temp = 10000 + 10000;
    temp = sqrt(100);
    // temp = sqrt(1000);
    // temp = sqrt(10000);
  }
}

void func2(void) {
  int i, temp;
  for (i = 0; i < 1000; i++) {
    // temp = 100 * 100;
    temp = sqrt(100);
    temp = sqrt(1000);
    // temp = sqrt(10000);
  }
}

void func3(void) {
  int i, temp;
  for (i = 0; i < 10000; i++) {
    // temp = 100 + 100;
    temp = sqrt(100);
    temp = sqrt(1000);
    temp = sqrt(10000);
  }
}

void dummyFunction(void) {
  int startTime, endTime;
  startTime = micros();
  func1();
  endTime = micros();
  t1 = endTime - startTime;
  delay(100);
  startTime = micros();
  func2();
  endTime = micros();
  t2 = endTime - startTime;
  delay(100);
  startTime = micros();
  // func3();
  endTime = micros();
  t3 = endTime - startTime;
}

void loop() {
  int startTime, endTime;
  startTime = micros();
  Serial.println("Start testing...");
  dummyFunction();
  endTime = micros();
  Serial.print("t1: ");
  Serial.println(t1);
  Serial.print("t2: ");
  Serial.println(t2);
  Serial.print("t3: ");
  Serial.println(t3);
  Serial.print("total: ");
  Serial.println(endTime - startTime - 200 * 1000);
  delay(500);
  exit(0);
}
