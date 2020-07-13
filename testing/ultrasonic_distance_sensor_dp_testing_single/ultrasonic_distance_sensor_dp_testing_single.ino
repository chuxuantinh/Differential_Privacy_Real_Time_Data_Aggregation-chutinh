/* this code reads a distance value multiple times from a single sensor and runs the algorithm each time assuming that there is only one physical sensor
 */

#define DEBUG 1
#define INFO 1
#define PRINTEXECTIME 0
#define LOOPCOUNT 10
#define USELAPLACE 1
#define USEGAUSSIAN 0

#define NOISEMAGOUTSIDEFOR 1
#define NOISEMAGINSIDEFOR 0

/* mathematical constants
 */
const float e = 2.71828;
const float pi = 3.14159;

/* pin mapping
 */
const int echoPin = 2;
const int trigPin = 3;

const int splitCount = 2;
int duration;
int distanceFraction;
float distance, distanceAggregate, distanceSplit[splitCount], dpNoise;

const float epsilon = 0.1;
/* summation operation has been demonstrated, hence sensitivity for this operation i.e. aggregation
 */
const float sensitivityAggregation = 1.0;
const float magScale = 10.0;

/* laplace probability density function
 */
float laplace(float value, float mean, float b) {
  return pow(e, -(abs(value - mean) / b)) / (2 * b);
}

/* gaussian probability density function
 */
float gaussian(float value, float mean, float sigma) {
  return pow(e, -(pow((value - mean) / sigma, 2)) / 2) / (sigma * sqrt(2 * pi));
}

void setup() {
  /* setup code to run once
   */
  Serial.begin(9600);
  /* initializing pins
   */
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  /* put your main code to run repeatedly
   */
  int i = LOOPCOUNT, j;
  int startTime, endTime;
  int totalRandomForSplit = 0;
  float totalRandomForNoiseAdd = 0.0;
  float noiseLarge, noiseMag, noiseMagForRandom;
  /* initializing the pseudo-random generator on a fairly random input enabling values returned from random for the same range across executions of a sketch to differ
   */
  randomSeed(analogRead(5));
  while (i--) {
#if DEBUG
    Serial.print("Loop number -> ");
    Serial.println(LOOPCOUNT - i);
#endif
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    duration = pulseIn(echoPin, HIGH);
    /* speed of sound is .0343 cm/microsecond @ 20 degrees temperature
     */
    distance = (duration * .0343) / 2;
#if INFO
    Serial.print("Distance (in cm) before noise addition: ");
#endif
    Serial.println(distance);
    startTime = micros();
    /* due to low precision of float, the computed value of laplace/gaussian being in the order of 10^-9 is effectively getting stored as 0.0
     *  hence, instead of using the distance value as an argument to the laplace/gaussian pdf, a constant value of 1 is being used
     *  TODO
     *  check if the above workaround is valid or not
     *  check if this is how it is to be done i.e. sample using a constant value instead of using the actual sensor's output
     */
#if USELAPLACE
    // dpNoise = laplace(distance, 0.0, sensitivityAggregation / epsilon);
    dpNoise = laplace(1.0, 0.0, sensitivityAggregation / epsilon);
#elif USEGAUSSIAN
    // dpNoise = gaussian(distance, 0.0, sensitivityAggregation / epsilon);
    dpNoise = gaussian(1.0, 0.0, sensitivityAggregation / epsilon);
#else
    dpNoise = 0.0;
#endif
    endTime = micros();
#if DEBUG
    Serial.print("Noise added before splitting: ");
    Serial.println(dpNoise);
#endif
    distance += dpNoise;
#if DEBUG
    Serial.print("Distance (in cm) after noise addition before splitting: ");
    Serial.println(distance);
#endif
#if PRINTEXECTIME
    /* execution time required for the Laplace dp computation i.e. noise addition
     */
    Serial.print("Execution time (in microseconds) for noise addition before splitting: ");
    Serial.println(endTime - startTime);
#endif
    startTime = micros();
    /* splitting the distance value to get random splits
     */
    for (j = 0; j < splitCount; j++) {
      /* instead of upper limit of 1 in random, it can be any other number
       *  -> 1 won't work since random only returns integer values within the given range
       *  hence use any other higher integer
       */
      distanceFraction = random(0, 100);
      distanceSplit[j] = distance * distanceFraction;
      totalRandomForSplit += distanceFraction;
#if DEBUG
      Serial.print("distanceFraction: ");
      Serial.println(distanceFraction);
      Serial.print("distanceSplit: ");
      Serial.println(distanceSplit[j]);
      Serial.print("totalRandomForSplit: ");
      Serial.println(totalRandomForSplit);
#endif
    }
    for (j = 0; j < splitCount; j++) {
      distanceSplit[j] /= totalRandomForSplit;
#if DEBUG
      Serial.print("distanceSplit: ");
      Serial.println(distanceSplit[j]);
#endif
    }
    endTime = micros();
    totalRandomForSplit = 0;
#if PRINTEXECTIME
    /* execution time required for splitting
     */
    Serial.print("Execution time (in microseconds) for splitting: ");
    Serial.println(endTime - startTime);
#endif
#if DEBUG
    Serial.print("Splits of the measured distance: ");
    for (j = 0; j < splitCount; j++) {
      Serial.print(distanceSplit[j]);
      Serial.print("\t");
    }
    Serial.println("");
#endif
    startTime = micros();
    // noiseMag = distanceSplit[0] * magScale;
#if NOISEMAGOUTSIDEFOR
    noiseMag = (distance / splitCount) * magScale;
#endif
    // noiseMagForRandom = pow(noiseMag, 2);
#if DEBUG && NOISEMAGOUTSIDEFOR
    Serial.print("noiseMag: ");
    Serial.println(noiseMag);
    Serial.print("noiseMagForRandom: ");
    Serial.println(noiseMagForRandom);
#endif
    /* large noise addition to the random splits
     */
    for (j = 0; j < splitCount; j++) {
#if NOISEMAGINSIDEFOR
      noiseMag = distanceSplit[j] * magScale;
      noiseMagForRandom = pow(noiseMag, 2);
#endif
#if DEBUG && NOISEMAGINSIDEFOR
      Serial.print("noiseMag: ");
      Serial.println(noiseMag);
      Serial.print("noiseMagForRandom: ");
      Serial.println(noiseMagForRandom);
#endif
      /* this has been done to generate large random float noise
       *  large -> noiseMagForRandom i.e. square of noiseMag has been used to input large range to random and then division by relatively smaller term as mentioned below has been done
       *  float -> division by 2 * noiseMag has been done after calling random with large range as above
       */
#if NOISEMAGINSIDEFOR
      noiseLarge = random(-(int)noiseMagForRandom, (int)noiseMagForRandom) / (2 * noiseMag);
#elif NOISEMAGOUTSIDEFOR
      noiseLarge = random(-(int)noiseMag, (int)noiseMag) / (2 * sqrt(noiseMag));
#endif
      distanceSplit[j] += noiseLarge;
      totalRandomForNoiseAdd += noiseLarge;
#if DEBUG
      Serial.print("noiseLarge: ");
      Serial.println(noiseLarge);
      Serial.print("distanceSplit: ");
      Serial.println(distanceSplit[j]);
      Serial.print("totalRandomForNoiseAdd: ");
      Serial.println(totalRandomForNoiseAdd);
#endif
    }
    totalRandomForNoiseAdd /= splitCount;
#if DEBUG
    Serial.print("totalRandomForNoiseAdd after division by splitCount: ");
    Serial.println(totalRandomForNoiseAdd);
#endif
    if (totalRandomForNoiseAdd > 0) {
      for (j = 0; j < splitCount; j++) {
        distanceSplit[j] -= totalRandomForNoiseAdd;
#if DEBUG
        Serial.print("distanceSplit: ");
        Serial.println(distanceSplit[j]);
#endif
      }
    }
    else if (totalRandomForNoiseAdd < 0) {
      totalRandomForNoiseAdd = abs(totalRandomForNoiseAdd);
      for (j = 0; j < splitCount; j++) {
        distanceSplit[j] += totalRandomForNoiseAdd;
      }
    }
    endTime = micros();
    totalRandomForNoiseAdd = 0.0;
#if PRINTEXECTIME
    /* execution time required for noise addition after splitting
     */
    Serial.print("Execution time (in microseconds) for noise addition after splitting: ");
    Serial.println(endTime - startTime);
#endif
#if DEBUG
    Serial.print("Splits of the measured distance after adding large noise: ");
    for (j = 0; j < splitCount; j++) {
      Serial.print(distanceSplit[j]);
      Serial.print("\t");
    }
    Serial.println("");
#endif
    distanceAggregate = 0.0;
    startTime = micros();
    for (j = 0; j < splitCount; j++) {
      distanceAggregate += distanceSplit[j];
    }
    endTime = micros();
#if INFO
    Serial.print("Distance (in cm) after noise addition after splitting and post aggregation: ");
#endif
    Serial.println(distanceAggregate);
#if PRINTEXECTIME
    /* execution time required for aggregation
     */
    Serial.print("Execution time (in microseconds) for aggregation: ");
    Serial.println(endTime - startTime);
#endif
    delay(500);
  }
  exit(0);
}
