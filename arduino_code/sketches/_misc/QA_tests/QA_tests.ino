// QA Testing to make sure all sensors work
#include <PID_v1.h>
#define ENC_CHAN_A 18
#define ENC_CHAN_B 19
#define ENC_PROP_A 2
#define ENC_PROP_B 21
#define DIR_A 12
#define DIR_B 13
#define PWM_A 3
#define PWM_B 11
#define PPR 600 //pulses per revolution of the encoder
#define PWM_MAX 125

volatile int prop_count_a=0; //Prop A Counter
volatile int prop_count_b=0; //Prop B Counter

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  
  //Initialize pins for optical sensors
  pinMode(ENC_PROP_A, INPUT);
  pinMode(ENC_PROP_B, INPUT);
  
  attachInterrupt(digitalPinToInterrupt(ENC_PROP_A), do_prop_count_a, RISING);
  attachInterrupt(digitalPinToInterrupt(ENC_PROP_B), do_prop_count_b, RISING);
}

void loop() {
  // put your main code here, to run repeatedly:
Serial.print("prop a: "); Serial.print(prop_count_a); Serial.print(" | prop b: "); Serial.println(prop_count_b);

}


void do_prop_count_a()
{
  prop_count_a++;
}

void do_prop_count_b()
{
  prop_count_b++;
}
