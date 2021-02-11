#include "g_code_interpreter.h"
SerialComms com();

//Encoder Params
#define PPR 600

//Interrupt variables
#define CHAN_A 18
#define CHAN_B 19
volatile int prev_count = 0;
volatile int current_count = 0;
volatile unsigned long prev_time = 0;
volatile unsigned long current_time = 0;
unsigned long zero_velocity_time_threshold = 250000;

void setup() {
  Serial.begin(115200);
  pinMode(CHAN_A, INPUT_PULLUP);
  pinMode(CHAN_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(CHAN_A), do_interrupt, RISING);
}

void loop() {
Serial.print("count: "); Serial.print(current_count); Serial.print(" velocity: "); Serial.println(calc_velocity());

if(micros() - current_time > zero_velocity_time_threshold) {prev_count = current_count;}
}

void do_interrupt()
{
  prev_time = current_time;//update previous time
  current_time = micros(); //get current microseconds
  prev_count = current_count; //update previous count
  if(digitalRead(CHAN_B) == HIGH)
  {
    current_count++; //if CHAN_B is high, increment current count
  }
  else { current_count--; } //else decrement current count
}

double calc_velocity()
{
  return (360.0/PPR)*(current_count - prev_count) / double((current_time - prev_time)/1000000.0);
//  return (current_time - prev_time);
}
