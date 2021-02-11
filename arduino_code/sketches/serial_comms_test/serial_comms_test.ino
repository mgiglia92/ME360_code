#include "SerialCommsBase.h"

#include <motor_control_hardware_config.h>
#include <PID_beard.h>
#include <Differentiator.h>


#define DEG_TO_RAD 2*3.14159/360
#define RPM_TO_RADS 0.104719755
#define DEGS_TO_RPM 0.166667

const int storage_length = 200;
int time[storage_length];

//Timing Parameters for fixed interval calculations for PID and derivitave
//unsigned long prev_micros = 0;
//unsigned long current_micros;
//double sample_period = 0.005; //in sec

// NEED TO ADD METHOD TO SELECT WHICH TYPE OF LAB IS BEING DONE
SerialComms com(sample_period);  // Serial Communications class instantiation


//double sigma = 0.01;
//Differentiator diff(sigma, sample_period);

//***********************************************************************************
void setup() {
  Serial.begin(57600);  // Begins Serial communication
  char test_string[]{"S5,T20,H1242.234,"};
  Serial.println(test_string);
  Serial.println(com.sample_period, 4);
  Serial.println(com.lab_code);
  Serial.println(com.get_cmd_code(test_string, 'S', -1));
  Serial.println(com.get_cmd_code(test_string, 'T', -2));
  Serial.println(com.get_cmd_code(test_string, 'H', -3), 5);
  Serial.println(com.get_cmd_code(test_string, 'Z', -4));
  Serial.println("This is a test");
}

//***********************************************************************************
void loop() {  
   if (com.cmd_index == 1){
      Serial.print("Start: "); Serial.println(micros());
   }
   com.retrieve_cmd();
   if (com.cmd_index == 0){
    Serial.print("End: "); Serial.println(micros());
    Serial.println(com.cmd_string);
  }
  delay(100);
}
