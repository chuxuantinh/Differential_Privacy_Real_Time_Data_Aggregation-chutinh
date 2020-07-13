/* this code reads a heart rate value multiple times from a single xd58c pulse sensor and runs the algorithm only once after having read all the values assuming that every time the value has been read from a different pulse sensor i.e. this simulates the presence of multiple pulse sensors
 */

#include <PrintEx.h>
#include <SoftwareSerial.h>

#define USE_ARDUINO_INTERRUPTS true

#include <PulseSensorPlayground.h>

#define DEBUG 0
#define INFO 0

#define MAXSENSORCNT 45 // 5

#define CHGEPS 0
#define CHGSENSORCNT 1

const int OUTPUT_TYPE = SERIAL_PLOTTER;
const int PULSE_INPUT = A0;
const int PULSE_BLINK = 13;
const int THRESHOLD = 550;

PulseSensorPlayground pulseSensor;

SoftwareSerial mySoftwareSerial(6, 7);

StreamEx mySerial = Serial;

const int splitCount = 2;
int sensorCount = MAXSENSORCNT;
int heartRate[MAXSENSORCNT];
float heartRateFraction, partialHeartRateSum, heartRateSplit[MAXSENSORCNT][splitCount], heartRateDpNoise[MAXSENSORCNT];
float tempHeartRateSplit[MAXSENSORCNT];

int execTimeNoiseAddBeforeSplitLaplace, execTimeNoiseAddBeforeSplitGaussian;
int execTimeSplit, execTimeNoiseAddAfterSplit, execTimePartialSums;
int execTimeTotalLaplace, execTimeTotalGaussian;
int communicationTime;

float epsilon = 0.1;
const float sensitivitySummation = 220.0;
const float magScale = 10.0;

float readFloatFromSerial(void) {
  String floatStr = "";
  char readByte;
  do {
    readByte = mySoftwareSerial.read();
    if ((int)readByte != -1) {
     floatStr += String(readByte);
    }
  } while (readByte != '\n');
  return floatStr.toFloat();
}

float exp_sample(float scale) {
  return -scale * log(random(1, 500) / 499.0);
}

float laplace(float scale) {
  return exp_sample(scale) - exp_sample(scale);
}

float gaussian(float u, float var) {
  float r1 = random(1, 500) / 499.0;
  float r2 = random(1, 500) / 499.0;
  return u + var * cos(2 * PI * r1) * sqrt(-2 * log(r2));
}

void addNoiseHeartRate(char noiseType) {
  int i;
  if (noiseType == 'l') {
    for (i = 0; i < sensorCount; i++) {
      heartRateDpNoise[i] = (float)heartRate[i] + laplace(sensitivitySummation / epsilon);
    }
  }
  else if (noiseType == 'g') {
    for (i = 0; i < sensorCount; i++) {
      heartRateDpNoise[i] = (float)heartRate[i] + gaussian(0.0, sensitivitySummation / epsilon);
    }
  }
  else {
    for (i = 0; i < sensorCount; i++) {
      heartRateDpNoise[i] = (float)heartRate[i];
    }
  }
}

void splitHeartRates(void) {
  int i, j;
  float totalRandom;
  for (i = 0; i < sensorCount; i++) {
    totalRandom = 0.0;
    for (j = 0; j < splitCount; j++) {
      heartRateFraction = random(0, 100);
      heartRateSplit[i][j] = heartRateDpNoise[i] * heartRateFraction;
      totalRandom += heartRateFraction;
    }
    for (j = 0; j < splitCount; j++) {
      heartRateSplit[i][j] /= totalRandom;
    }
  }
}

void addNoiseHeartRateSplits(void) {
  int i, j;
  float totalRandom, noiseLarge, noiseMag;
  for (i = 0; i < sensorCount; i++) {
    totalRandom = 0.0;
    noiseMag = (heartRate[i] / splitCount) * magScale;
    for (j = 0; j < splitCount; j++) {
      noiseLarge = random(-(int)noiseMag, (int)noiseMag) / (2.0 * sqrt(noiseMag));
      if (isnan(noiseLarge)) {
        noiseLarge = 0.0;
      }
      heartRateSplit[i][j] += noiseLarge;
      totalRandom += noiseLarge;
    }
    totalRandom /= splitCount;
    if (totalRandom > 0.0) {
      for (j = 0; j < splitCount; j++) {
        heartRateSplit[i][j] -= totalRandom;
      }
    }
    else if (totalRandom < 0.0) {
      totalRandom = abs(totalRandom);
      for (j = 0; j < splitCount; j++) {
        heartRateSplit[i][j] += totalRandom;
      }
    }
  }
}

void computePartialHeartRateSums(void) {
  int i, j;
  partialHeartRateSum = 0.0;
  for (i = 0; i < splitCount; i++) {
    for (j = 0; j < sensorCount; j++) {
      partialHeartRateSum += heartRateSplit[j][i];
    }
  }
}

void algorithm(char noiseType) {
  int i;
  int startTime, endTime;
  startTime = micros();
  addNoiseHeartRate(noiseType);
  endTime = micros();
  if (noiseType == 'l') {
    execTimeNoiseAddBeforeSplitLaplace = endTime - startTime;
  }
  else if (noiseType == 'g') {
    execTimeNoiseAddBeforeSplitGaussian = endTime - startTime;
  }
  else {
    execTimeNoiseAddBeforeSplitLaplace = -1.0;
    execTimeNoiseAddBeforeSplitGaussian = -1.0;    
  }
  startTime = micros();
  splitHeartRates();
  endTime = micros();
  execTimeSplit = endTime - startTime;
  startTime = micros();
  addNoiseHeartRateSplits();
  endTime = micros();
  execTimeNoiseAddAfterSplit = endTime - startTime;
  startTime = micros();
#if DEBUG
  for (i = 0; i < sensorCount; i++) {
    mySerial.printf("Noised heart rate splits on green arduino before getting noised heart rate splits from blue arduino for sensor %d -> %.2f %.2f\n", i + 1, heartRateSplit[i][0], heartRateSplit[i][1]);
  }
#endif
  for (i = 0; i < sensorCount; i++) {
    tempHeartRateSplit[i] = readFloatFromSerial();
  }
  mySoftwareSerial.begin(4800);
  delay(500);
  for (i = 0; i < sensorCount; i++) {
    mySoftwareSerial.println(heartRateSplit[i][1]);
    heartRateSplit[i][1] = tempHeartRateSplit[i];
  }
  mySoftwareSerial.begin(2400);
#if DEBUG
  for (i = 0; i < sensorCount; i++) {
    mySerial.printf("Noised heart rate splits on green arduino after getting noised heart rate splits from blue arduino for sensor %d -> %.2f %.2f\n", i + 1, heartRateSplit[i][0], heartRateSplit[i][1]);
  }
#endif
  endTime = micros();
  communicationTime = endTime - startTime;
  startTime = micros();
  computePartialHeartRateSums();
  endTime = micros();
  execTimePartialSums = endTime - startTime;
}

void setup() {
  Serial.begin(9600);
  mySoftwareSerial.begin(2400);

  pulseSensor.analogInput(PULSE_INPUT);
  pulseSensor.setSerial(Serial);
  pulseSensor.setOutputType(OUTPUT_TYPE);
  pulseSensor.setThreshold(THRESHOLD);

  if (!pulseSensor.begin()) {
    for(;;) {
      digitalWrite(PULSE_BLINK, LOW);
      delay(50);
      digitalWrite(PULSE_BLINK, HIGH);
      delay(50);
    }
  }
}

void loop() {
  int i, j;
  int startTime, endTime;
  int beatsPerMinute;
#if INFO
  mySerial.printf("Sensitivity value for summation operation: %.2f\n", sensitivitySummation);
#else
  mySerial.printf("%.2f\n", sensitivitySummation);
#endif
#if CHGSENSORCNT
#if INFO
  mySerial.printf("Epsilon value: %.2f\n", epsilon);
#else
  mySerial.printf("%.2f\n", epsilon);
#endif
#elif CHGEPS
#if INFO
  mySerial.printf("Number of sensors: %d\n", sensorCount);
#else
  mySerial.printf("%d\n", sensorCount);
#endif
#else
#if INFO
  mySerial.printf("Epsilon value: %.2f\n");
#else
  mySerial.printf("%.2f\n", epsilon);
#endif
#if INFO
  mySerial.printf("Number of sensors: %d\n", sensorCount);
#else
  mySerial.printf("%d\n", sensorCount);
#endif
#endif
#if CHGEPS
  epsilon = 0.0;
  while ((int)(epsilon + 0.5) != 3) { // 2
#if INFO
    mySerial.printf("Epsilon value: %.2f\n", epsilon);
#else
    mySerial.printf("%.2f\n", epsilon);
#endif
    if ((int)(epsilon * 10) == 0) {
        epsilon = 0.1;
    }
#elif CHGSENSORCNT
  sensorCount = 5;
  while (sensorCount != 50) { // 20, 30, 40
#if INFO
    mySerial.printf("Number of sensors: %d\n", sensorCount);
#else
    mySerial.printf("%d\n", sensorCount);
#endif
#else
  int runOnce = 1;
  while (runOnce) {
#endif
    i = 0;
    partialHeartRateSum = 0.0;
    randomSeed(analogRead(5));
    while (i++ != sensorCount) {
      beatsPerMinute = pulseSensor.outputSample();
      while (beatsPerMinute < 1 || beatsPerMinute > 219) {
        for (j = 0; j < 25; j++) {
          digitalWrite(PULSE_BLINK, LOW);
          delay(100);
          digitalWrite(PULSE_BLINK, HIGH);
          delay(100);
        }
        beatsPerMinute = pulseSensor.outputSample();
      }
      heartRate[i - 1] = beatsPerMinute;
      partialHeartRateSum += (float)heartRate[i - 1];
#if DEBUG
      mySerial.printf("Heart rate (in bpm) before noise addition: %d\n", heartRate[i - 1]);
#endif
      delay(500);
    }
    Serial.begin(9600);
#if INFO
    mySerial.printf("Partial sum of heart rate (in bpm) before noise addition: %d\n", (int)partialHeartRateSum);
#else
    mySerial.printf("%d\n", (int)partialHeartRateSum);
#endif
    startTime = micros();
    algorithm('l');
    endTime = micros();
    execTimeTotalLaplace = endTime - startTime - communicationTime;
    delay(500);
#if INFO
    mySerial.printf("Partial sum of heart rate (in bpm) after noise addition using laplace after splitting: %.2f\n", partialHeartRateSum);
#else
    mySerial.printf("%.2f\n", partialHeartRateSum);
#endif
    startTime = micros();
    algorithm('g');
    endTime = micros();
    execTimeTotalGaussian = endTime - startTime - communicationTime;
    delay(500);
#if INFO
    mySerial.printf("Partial sum of heart rate (in bpm) after noise addition using gaussian after splitting: %.2f\n", partialHeartRateSum);
#else
    mySerial.printf("%.2f\n", partialHeartRateSum);
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for noise addition using laplace before splitting: %d\n", abs(execTimeNoiseAddBeforeSplitLaplace));
#else
    mySerial.printf("%d\n", abs(execTimeNoiseAddBeforeSplitLaplace));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for noise addition using gaussian before splitting: %d\n", abs(execTimeNoiseAddBeforeSplitGaussian));
#else
    mySerial.printf("%d\n", abs(execTimeNoiseAddBeforeSplitGaussian));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for splitting: %d\n", abs(execTimeSplit));
#else
    mySerial.printf("%d\n", abs(execTimeSplit));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for noise addition after splitting: %d\n", abs(execTimeNoiseAddAfterSplit));
#else
    mySerial.printf("%d\n", abs(execTimeNoiseAddAfterSplit));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for partial summations: %d\n", abs(execTimePartialSums));
#else
    mySerial.printf("%d\n", abs(execTimePartialSums));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for the complete algorithm using laplace: %d\n", abs(execTimeTotalLaplace));
#else
    mySerial.printf("%d\n", abs(execTimeTotalLaplace));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for the complete algorithm using gaussian: %d\n", abs(execTimeTotalGaussian));
#else
    mySerial.printf("%d\n", abs(execTimeTotalGaussian));
#endif
    delay(500);
#if CHGEPS
    if ((int)(epsilon * 10) == 1) {
      epsilon = 0.0;
    }
    epsilon += 0.5;
#elif CHGSENSORCNT
    sensorCount += 5;
#else
    runOnce -= 1;
#endif
  }
  exit(0);
}
