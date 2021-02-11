#include <Arduino.h>
#include <PID_v1.h>

#define ENC_CHAN_A 18
#define ENC_CHAN_B 19
#define DIR_A 12
#define DIR_B 13
#define PWM_A 3
#define PWM_B 11
#define BRK_A 9
#define BRK_B 8
#define PPR 600 //pulses per revolution of the encoder

//Global Variables
//Encoder Counting Variables, Encoder Parameters
long enc_count = 0; //Encoder counting variable
float deg = 0;    // Angle rotated
float start_time = 0;

////PID controller variables
double input;
double motorPWM = 0.0;
double setpoint=1000;
double kp = 0.5; // 0.12 was sort of stable
double ki = 0;
double kd = 0;
int base_pwm = 50; //Default power for both propellers

int count = 0;

int main(void){
  init();
  #if defined(USBCON)
      USBDevice.attach();
  #endif
  Serial.begin(9600);
  
  //Setup  
  //Set digial pin modes
  pinMode(ENC_CHAN_A, INPUT_PULLUP);
  pinMode(ENC_CHAN_B, INPUT_PULLUP);
  pinMode(PWM_A, OUTPUT);
  pinMode(PWM_B, OUTPUT);
  pinMode(DIR_A, OUTPUT);
  pinMode(DIR_B, OUTPUT);
  digitalWrite(BRK_B,HIGH);  // Prevent Motor Rotate
  //Set interrupt connection
  attachInterrupt(digitalPinToInterrupt(ENC_CHAN_A), do_count, RISING);
  //Setup PID
  PID anglePID(&input, &motorPWM, &setpoint, kp, ki, kd, DIRECT);
  anglePID.SetOutputLimits(-225,225);
  anglePID.SetMode(AUTOMATIC);
  digitalWrite(BRK_B, LOW);   //Disengage the Brake for Channel B
//  Serial.println(count);

  //Handshake
//  while(!Serial.available()){Serial.println('A');delay(300);}
//  if(Serial.read() == 'A'){delay(1000);}
////  {Serial.println("Contact established");delay(1000);}

  start_time = micros();
  while(1){
    input = double(enc_count);
    anglePID.Compute();
    if(motorPWM<0){                         // Spins motor in reverse direction
      digitalWrite(DIR_B,HIGH);
      analogWrite(PWM_B,abs(motorPWM));}
    else{                                   // Spins motor in forward direction
      digitalWrite(DIR_B,LOW);
      analogWrite(PWM_B,motorPWM);}
    print_enc_count();
    count = count + 1;
    if(micros() - start_time > 10000000){break;}
  }
  if(Serial.available()){Serial.print("-1,-1,");Serial.println(count);delay(10);}; // Prints how many times this loop was executed
  digitalWrite(PWM_B,LOW); // Stops Motor
  while(1){Serial.println("End");delay(300);}
}

void do_count(){
  if(digitalRead(ENC_CHAN_B) == 1){enc_count++;} //If chan B is HIGH, increment
  else {enc_count--;} //Else decrement
}

void print_enc_count(){
  float cur_time = micros();
//  if(Serial.read() == 'B'){
      Serial.print(cur_time-start_time);
      Serial.print(",");
      Serial.print(enc_count);
      Serial.print(",");
      Serial.println(motorPWM);
//    }
}
