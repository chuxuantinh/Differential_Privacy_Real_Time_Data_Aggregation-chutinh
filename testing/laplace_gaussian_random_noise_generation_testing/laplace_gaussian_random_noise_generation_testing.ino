#include <Gaussian.h>

void setup() {
  Serial.begin(9600);
}

float exp_sample(float scale) {
  return -scale * log(random(1, 10000) / 9999.0);
}

int sign(float value) {
  if (value > 0.0) {
    return 1;
  }
  else if (value < 0.0) {
    return -1;
  }
  return 0;
}

int randSign() {
  int value = random(-1, 2);
  while (value != -1 && value != 1) {
    value = random(-1, 2);
  }
  return value;
}

float laplace(float scale) {
  return exp_sample(scale) - exp_sample(scale);
}

/*
float laplace(float scale) {
  float value = random(-5000, 5000) / 9999.0;
  return scale * sign(value) * log(1 - 2 * abs(value));
}
*/

/*
float laplace(float scale) {
  return exp_sample(scale) * randSign();
}
*/

float gaussian(float u, float var) {
  float r1 = random(0, 10000) / 9999.0;
  float r2 = random(0, 10000) / 9999.0;
  return u + var * cos(2 * PI * r1) * sqrt(-log(r2));
}

void loop() {
  randomSeed(analogRead(5));
  Gaussian myGaussian = Gaussian(0.0, sq(400.0 / 0.1));
  for (int i = 0; i < 500; i++) {
    Serial.println(laplace(400.0 / 0.1));
    // Serial.println(myGaussian.random());
    // Serial.println(gaussian(0.0, (400.0 / 0.1)));
    // Serial.println(random(0, 10000) / 9999.0);
  }
  exit(0);
}
