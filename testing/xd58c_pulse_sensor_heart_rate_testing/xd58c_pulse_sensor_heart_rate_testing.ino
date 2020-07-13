#define USE_ARDUINO_INTERRUPTS true
#include <PulseSensorPlayground.h>
#include <PrintEx.h>

StreamEx mySerial = Serial;

const int OUTPUT_TYPE = SERIAL_PLOTTER;

const int PULSE_INPUT = A0;
const int PULSE_BLINK = 13;
const int PULSE_FADE = 5;
const int THRESHOLD = 550;

PulseSensorPlayground pulseSensor;

void setup() {
  Serial.begin(115200);

  pulseSensor.analogInput(PULSE_INPUT);
  pulseSensor.blinkOnPulse(PULSE_BLINK);
  pulseSensor.fadeOnPulse(PULSE_FADE);

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
  delay(1000);

  int beatsPerMinute = 0;

  beatsPerMinute = pulseSensor.outputSample();
  if (beatsPerMinute > 50 && beatsPerMinute < 150) {
    mySerial.printf("Heart rate (in bpm) = %d\n", beatsPerMinute);
  }

  if (pulseSensor.sawStartOfBeat()) {
   pulseSensor.outputBeat();
  }
}
