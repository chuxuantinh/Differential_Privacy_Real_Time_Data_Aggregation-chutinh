/* this code reads a heart rate value multiple times from a single MI Band 2 and runs the algorithm only once after having read all the values assuming that every time the value has been read from a different MI Band 2 i.e. this simulates the presence of multiple MI Bands
 */

#include <PrintEx.h>
#include <SoftwareSerial.h>

#define DEBUG 0
#define INFO 0

#define MAXSENSORCNT 45

#define CHGEPS 1
#define CHGSENSORCNT 0

SoftwareSerial mySoftwareSerial(6, 7);

StreamEx mySerial = Serial;

const int splitCount = 2;
int sensorCount = MAXSENSORCNT;
int heartRate[MAXSENSORCNT];
float heartRateFraction, partialHeartRateSum[splitCount], finalHeartRateSum, heartRateSplit[MAXSENSORCNT][splitCount], heartRateDpNoise[MAXSENSORCNT];

float execTimeNoiseAddBeforeSplitLaplace, execTimeNoiseAddBeforeSplitGaussian;
float execTimeSplit, execTimeNoiseAddAfterSplit, execTimePartialSums, execTimeFinalSum;
float execTimeTotalLaplace, execTimeTotalGaussian;

float epsilon = 0.1;
const float sensitivitySummation = 220.0;
const float magScale = 10.0;

float exp_sample(float scale) {
  return -scale * log(random(1, 100) / 99.9);
}

float laplace(float scale) {
  return exp_sample(scale) - exp_sample(scale);
}

float gaussian(float u, float var) {
  float r1 = random(0, 500) / 499.0;
  float r2 = random(0, 500) / 499.0;
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
  for (i = 0; i < splitCount; i++) {
    partialHeartRateSum[i] = 0.0;
  }
  for (i = 0; i < splitCount; i++) {
    for (j = 0; j < sensorCount; j++) {
      partialHeartRateSum[i] += heartRateSplit[j][i];
    }
  }
}

void computeFinalHeartRateSum(void) {
  int i;
  finalHeartRateSum = 0.0;
  for (i = 0; i < splitCount; i++) {
    finalHeartRateSum += partialHeartRateSum[i];
  }
}

void algorithm(char noiseType) {
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
  computePartialHeartRateSums();
  endTime = micros();
  execTimePartialSums = endTime - startTime;
  startTime = micros();
  computeFinalHeartRateSum();
  endTime = micros();
  execTimeFinalSum = endTime - startTime;
}

int readIntFromSerial(void) {
  String intStr = "";
  char readByte;
  do {
    readByte = mySoftwareSerial.read();
    if ((int)readByte != -1) {
     intStr += String(readByte);
    }
  } while (readByte != '\n');
  return intStr.toInt();
}

void setup() {
  Serial.begin(115200);
  mySoftwareSerial.begin(9600);
}

void loop() {
  int i;
  int startTime, endTime;
  float centralSumLaplace, centralSumGaussian;
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
  while ((int)(epsilon + 0.5) != 3) {
#if INFO
    mySerial.printf("Epsilon value: %.2f\n", epsilon);
#else
    mySerial.printf("%.2f\n", epsilon);
    if ((int)(epsilon * 10) == 0) {
        epsilon = 0.1;
    }
#endif
#elif CHGSENSORCNT
  sensorCount = 5;
  while (sensorCount != 50) {
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
    finalHeartRateSum = 0.0;
    randomSeed(analogRead(5));
#if INFO
    Serial.println("Sending HRM req");
#endif
    mySoftwareSerial.println("hrmReq");
#if INFO
    Serial.println("Sent HRM req");
#endif
    while (i++ != sensorCount) {
      heartRate[i - 1] = readIntFromSerial();
      finalHeartRateSum += (float)heartRate[i - 1];
#if DEBUG
      mySerial.printf("Heart rate (in bpm) before noise addition: %d\n", heartRate[i - 1]);
#endif
      delay(500);
    }
#if INFO
    mySerial.printf("Sum of heart rate (in bpm) before noise addition: %.2f\n", finalHeartRateSum);
#else
    mySerial.printf("%.2f\n", finalHeartRateSum);
#endif
    centralSumLaplace = finalHeartRateSum + laplace(sensitivitySummation / epsilon);
    centralSumGaussian = finalHeartRateSum + gaussian(0.0, sensitivitySummation / epsilon);
    delay(500);
#if INFO
    mySerial.printf("Sum of heart rate (in bpm) after direct noise addition using laplace post summation: %.2f\n", centralSumLaplace);
#else
    mySerial.printf("%.2f\n", centralSumLaplace);
#endif
#if INFO
    mySerial.printf("Sum of heart rate (in bpm) after direct noise addition using gaussian post summation: %.2f\n", centralSumGaussian);
#else
    mySerial.printf("%.2f\n", centralSumGaussian);
#endif
    startTime = micros();
    algorithm('l');
    endTime = micros();
    execTimeTotalLaplace = endTime - startTime;
    delay(500);
#if INFO
    mySerial.printf("Sum of heart rate (in bpm) after noise addition using laplace after splitting and post summation: %.2f\n", finalHeartRateSum);
#else
    mySerial.printf("%.2f\n", finalHeartRateSum);
#endif
    delay(500);
    startTime = micros();
    algorithm('g');
    endTime = micros();
    execTimeTotalGaussian = endTime - startTime;
    delay(500);
#if INFO
    mySerial.printf("Sum of heart rate (in bpm) after noise addition using gaussian after splitting and post summation: %.2f\n", finalHeartRateSum);
#else
    mySerial.printf("%.2f\n", finalHeartRateSum);
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for noise addition using laplace before splitting: %.2f\n", abs(execTimeNoiseAddBeforeSplitLaplace));
#else
    mySerial.printf("%.2f\n", abs(execTimeNoiseAddBeforeSplitLaplace));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for noise addition using gaussian before splitting: %.2f\n", abs(execTimeNoiseAddBeforeSplitGaussian));
#else
    mySerial.printf("%.2f\n", abs(execTimeNoiseAddBeforeSplitGaussian));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for splitting: %.2f\n", abs(execTimeSplit));
#else
    mySerial.printf("%.2f\n", abs(execTimeSplit));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for noise addition after splitting: %.2f\n", abs(execTimeNoiseAddAfterSplit));
#else
    mySerial.printf("%.2f\n", abs(execTimeNoiseAddAfterSplit));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for partial summations: %.2f\n", abs(execTimePartialSums));
#else
    mySerial.printf("%.2f\n", abs(execTimePartialSums));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for final summation: %.2f\n", abs(execTimeFinalSum));
#else
    mySerial.printf("%.2f\n", abs(execTimeFinalSum));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for the complete algorithm using laplace: %.2f\n", abs(execTimeTotalLaplace));
#else
    mySerial.printf("%.2f\n", abs(execTimeTotalLaplace));
#endif
    delay(500);
#if INFO
    // mySerial.printf("Execution time (in microseconds) for the complete algorithm using gaussian: %.2f\n", abs(execTimeTotalGaussian));
#else
    mySerial.printf("%.2f\n", abs(execTimeTotalGaussian));
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
