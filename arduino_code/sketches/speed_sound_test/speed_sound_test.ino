#include "SerialComms.h"
#include <ADC.h>

//ADC Settings
ADC *adc = new ADC(); //adc object

// Serial comms global var
SerialComms ser;
int daq_in_index=0;

//Timing variables
unsigned long current=0;
unsigned long prev=0;
unsigned long delta;
unsigned long delay_start_time=0; // Time when delay needs to be started (us)
bool delay_started=false; // Have we started the delay timer flag


//LED indication variables
const int led_pin = 13;
const unsigned long blink_duration = 500000; //500k us = 0.1sec

void setup() {
  //Setup adc settings
  adc->adc0->setAveraging(4); // set number of averages
  adc->adc0->setResolution(12); // set bits of resolution
  adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::HIGH_SPEED); // ,  change the conversion speed
  adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED); // change the sampling speed
  
  //Set led_pin to output
  pinMode(led_pin, OUTPUT);
  digitalWrite(led_pin, HIGH);

  //Begin serial communication
  Serial.begin(115200); 
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
    //Read analog ports
    ser.mic1[daq_in_index] = adc->adc0->analogRead(A0);
    ser.mic2[daq_in_index] = adc->adc0->analogRead(A1);
    ser.temp = adc->adc0->analogRead(A2);
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
    
    //Make led solid on
    digitalWrite(led_pin, HIGH);

    //Compare current time to delay time, if >= desired, return true, else reutrn false
    if((current - delay_start_time) >= ser.record_delay*1000000){return true;}
    else{return false;}
  }
  else{
    //If not make led blink
    //Check modulo of current and blink duration, if less than 100k turn off led, else on
    if((current%blink_duration) < 100000){digitalWrite(led_pin,LOW);}
    else { digitalWrite(led_pin, HIGH); }

    //Reset delay_started
    delay_started=false;
    return false;
  }
}
