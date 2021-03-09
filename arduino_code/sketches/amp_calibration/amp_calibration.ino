#include <ADC.h>
#include <MPU6050.h>

MPU6050 IMU(A4,A5);

//ADC Settings
ADC *adc = new ADC(); //adc object

unsigned long current=0;
unsigned long prev_led=0;
unsigned long prev=0;
unsigned long delta;
unsigned long delay_start_time=0; // Time when delay needs to be started (us)
bool delay_started=false; // Have we started the delay timer flag

//LED indication variables
const int led_pin = 13;

const unsigned long blink_duration = 50000; // 0.1sec
int ledState = LOW;

int straingage;
double accel;

float fs = 1000;
float dt = 1/fs;

void setup() {
  //Setup adc settings
  adc->adc0->setAveraging(0); // set number of averages
  adc->adc0->setResolution(12); // set bits of resolution
  adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::HIGH_SPEED); // ,  change the conversion speed
  adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED); // change the sampling speed

  IMU.initialize();
  //Set led_pin to output
  pinMode(led_pin, OUTPUT);
    
  //Begin serial communication
  Serial.begin(115200);

  for (int ii = 0; ii < 5; ii++){
    if (ledState == LOW){
      ledState = HIGH;
    }
    else if (ledState == HIGH){
      ledState = LOW;
    }
    digitalWrite(led_pin, ledState);
    delay(250);
  }

}

void loop() {
  // put your main code here, to run repeatedly:
  current = micros();
  delta = current - prev;//get delta from previous sample time
  if(delta>=dt*1000000.0) //if at or above desired sample time
  {
    IMU.update();
    prev = current;
    straingage = adc->adc0->analogRead(A0);
    accel = IMU.get_accel('z');
    Serial.print(100);Serial.print(',');
    Serial.print(4000);Serial.print(',');
    //Serial.println(accel,10);
    Serial.println(straingage);
  }
}
