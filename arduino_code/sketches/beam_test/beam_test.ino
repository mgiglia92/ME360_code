#include "SerialComms.h"
#include <MPU6050.h>
#include <ADC.h>

//ADC Settings
ADC *adc = new ADC(); //adc object

// Serial comms global var
SerialComms ser;
int daq_in_index=0;

//Timing variables
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

MPU6050 IMU(A4,A5);

void setup() {
  //Setup adc settings
  adc->adc0->setAveraging(4); // set number of averages
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
  // Check in serial buffer for command, handle if cmd exists
  ser.handle_command();
  // Check if time between samples has been reached, also check delay
  // acquire data
  if(discrete_timing() && check_delay()) { DAQ_in(); }
  // Print data to serial monitor
  DAQ_out();

}

//Print data to serial monitor
void DAQ_out()
{
    ser.send_data();
}

// Record data if start_reading flag is activated
void DAQ_in()
{
  //check if start reading
  if(ser.start_reading)
  {
    IMU.update();
    //Read analog ports
    ser.mic1[daq_in_index] = adc->adc0->analogRead(A0);
    ser.mic2[daq_in_index] = (IMU.get_accel('z')*10000);
    //ser.temp = adc->adc0->analogRead(A3);
    //print debug
//    Serial.println(ser.mic1[daq_in_index]);
    //increment index
    daq_in_index++;
    //Check if at end of array, shut off reading if so
    if(daq_in_index == ser.N) { daq_in_index = 0; ser.start_reading = 0;}
  }
}

// Check if the timing between samples has been reached.
bool discrete_timing()
{
  current = micros(); //get current micros
  delta = current - prev;//get delta from previous sample time
  if(delta>=ser.dt*1000000.0) //if at or above desired sample time
  {
    prev = current;
    return true;
  }
  else{return false;}
}

bool check_delay()
{
  //Check if recording has started, if so, start timing delay, make led solid
  if(ser.start_reading)
  {
    //If delay not started, start delay, set delay start time
    if(!delay_started){delay_start_time = current; delay_started=true;}
    else {
      if ((current-delay_start_time) < ser.record_delay*1000000){
        if((current-prev_led)>=blink_duration){
          prev_led = current;
          if (ledState == LOW){
            ledState = HIGH;
          }
          else if (ledState == HIGH){
            ledState = LOW;
          }
        }
      }
      else { ledState = HIGH; }
    }
    digitalWrite(led_pin,ledState);

    //Compare current time to delay time, if >= desired, return true, else reutrn false
    if((current - delay_start_time) >= ser.record_delay*1000000){return true;}
    else{return false;}
  }
  else{
    //If not make led blink
    //Check modulo of current and blink duration, if less than 100k turn off led, else on
    ledState = LOW;
    digitalWrite(led_pin, ledState);

    //Reset delay_started
    delay_started=false;
    return false;
  }
}
