#include <Arduino.h>
#include <PID_v1.h>
#include <g_code_interpreter.h>

#define ENC_A 2
#define ENC_B 3
#define DIR_B 13
#define PWM_B 11
#define BRK_B 8
#define PPR 211.2 //pulses per revolution of the encoder

//Global Variables
//Encoder Counting Variables, Encoder Parameters
float enc_count = 0; //Encoder rotation in raw counts
double enc_degree = 0;   //Encoder rotation in degrees
float start_time = 0;

////PID controller variables
double motorPWM = 0.0;
double setpoint=360;
double kp = 0.6;
double ki = 0.5;
double kd = 0.15;

int main(void){
  init();
  #if defined(USBCON)
      USBDevice.attach();
  #endif
  Serial.begin(9600);
  digitalWrite(BRK_B,HIGH);  // Prevent Motor Rotate
  
  //Setup  
  //Encoder Setup
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENC_A), Arise, RISING);
  attachInterrupt(digitalPinToInterrupt(ENC_A), Afall, FALLING);
  attachInterrupt(digitalPinToInterrupt(ENC_B), Brise, RISING);
  attachInterrupt(digitalPinToInterrupt(ENC_B), Bfall, FALLING);

  //Motor Setup
  pinMode(PWM_B, OUTPUT);
  pinMode(DIR_B, OUTPUT);

  
  //Setup PID
  PID anglePID(&enc_degree, &motorPWM, &setpoint, kp, ki, kd, DIRECT);
//  PID(&Input, &Output, &Setpoint, Kp, Ki, Kd, Direction)
  anglePID.SetOutputLimits(-225,225);
  anglePID.SetMode(AUTOMATIC);
//  Serial.println(count);

  //Handshake
//  while(!Serial.available()){Serial.println('A');delay(300);}
//  if(Serial.read() == 'A'){delay(1000);}
////  {Serial.println("Contact established");delay(1000);}

  start_time = micros();
  digitalWrite(BRK_B, LOW);   //Disengage the Brake for Channel B
  
  while(1){
    enc_degree = enc_count / PPR *360; //Converts encoder raw counts to degrees
    anglePID.Compute();
    if(motorPWM<0){                         // Spins motor in reverse direction
      digitalWrite(DIR_B,LOW);
      analogWrite(PWM_B,abs(motorPWM));}
    else{                                   // Spins motor in forward direction
      digitalWrite(DIR_B,HIGH);
      analogWrite(PWM_B,motorPWM);}
    print_enc_degree();
//    if(micros() - start_time > 10000000){break;}
  }
  digitalWrite(BRK_B,HIGH); // Stops Motor
//  while(1){Serial.println("End");delay(300);}
}

void print_enc_degree(){
  float cur_time = micros();
  if(Serial.read() == 'B'){
      Serial.print(cur_time-start_time);
      Serial.print(",");
      Serial.print(enc_degree);
      Serial.print(",");
      Serial.println(motorPWM);
    }
}



//Encoder interrupts
void Arise() {
  if(digitalRead(ENC_B) == LOW){enc_count ++;}
  else{enc_count --;}
}

void Afall() {
  if(digitalRead(ENC_B) == HIGH){enc_count ++;}
  else{enc_count --;}
}

void Brise() {
  if(digitalRead(ENC_A) == HIGH){enc_count ++;}
  else{enc_count --;}
}

void Bfall() {  
  if(digitalRead(ENC_A) == LOW){enc_count ++;}
  else{enc_count --;}
}
