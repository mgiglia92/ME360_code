#include "SerialComms.h"
//#include <string.h>
#include <PID_v1.h>
#include <drone_control_hardware_config.h>

unsigned long DELTA_T = 50000; //delta T in us between calculating velocity

//Global Variables
char incoming_char; //Serial incoming character for "parallel processing" of serial data
char cmd [200]; //Input command from serial
int cmd_index = 0; //Current index in cmd[] 
double input, motor_voltage, lowerOutputLimit, upperOutputLimit, setpoint, kp, ki, kd; // Controller params
int sampleTime, motor_direction;

double base_motor_voltage = 0;
volatile int enc_count;  //Encoder "ticks" counted, Enc ++ = CW, Enc -- = CCW
volatile double enc_deg; // Encoder position in degrees
double motor_speed; //Angular velocity of the motor
double motor_speed_array [MOVING_AVERAGE_SIZE]; //Array to allow averaging of motor speed to buffer motor_speed calculations
double prev_pos; //Previous encoder position for angular velocity calculation

//volatile int valA, valB;
volatile unsigned long prev_pulse_time, pulse_interval, prev_millis, current_millis;
int stationary_thresh = 80000; //80000 us threshold to set angular velocity to 0 if reached
double prev_motor_voltage;



SerialComms com;  //Serial Communications class instantiation

// Initialize PID motor controller
PID motor_controller(&input, &motor_voltage, &setpoint, kp, ki, kd, DIRECT);  // Set up PID controller


//***********************************************************************************
void setup() {
  Serial.begin(500000);  // Begins Serial communication

  //  com.mode = 1; // Default controller mode to automatic
  //  motor_controller.SetOutputLimits(-255,255); // Default controller to use full range of PWM

  //Encoder Setup
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), pulseA, CHANGE);
//  attachInterrupt(digitalPinToInterrupt(ENC_B), pulseB, CHANGE);

  //Motor Setup
  pinMode(PWM_A, OUTPUT);
  pinMode(DIR_A, OUTPUT);
  pinMode(PWM_B, OUTPUT);
  pinMode(DIR_B, OUTPUT);
  analogWrite(PWM_A, 0);
  analogWrite(PWM_B, 0); // Breaks Motor

  for (int i = 0; i < MOVING_AVERAGE_SIZE; i++) {
    motor_speed_array[i] = 0; //Initializing motor speed array
  }

  //Initialize variables
  current_millis = millis();
  prev_millis = current_millis;
  prev_pos = 0;
}

//***********************************************************************************

void loop() {
  update_controller_input();
  handle_command();  //Process incoming command
  enc_deg = double((enc_count / PPR) * 360);
  update_control_params();    //Update gains, update inputs based on labtype
  compute_motor_voltage(com.labType); // Compute motor voltage and write to motor
  send_data();
}

//*****************************************************//
// Arduino command handler
void handle_command() {
  if (Serial.available() != 0) {
    incoming_char = Serial.read();
    cmd[cmd_index] = incoming_char;
    if (incoming_char == '\0' || incoming_char == '%') {
      //      Serial.println("End of line, processing commands!");
      com.process_command(cmd);
      // Reset command buffer
      cmd_index = 0;
      memset(cmd, '\0', sizeof(cmd));
      update_control_params();   //Update gains, update inputs based on labtype
      
    }
    else {
      cmd_index ++;
    }
  }
}

//Update controller inputs
void update_controller_input()
{
    if (com.labType == 0) { // Angle Control
    input = enc_deg;
  }
  else if (com.labType == 1) { // Speed Control
    calc_motor_speed();
    input = motor_speed;
  }
}

//*****************************************************//
void update_control_params() {
//Check for Calibrate start
  if(com.calibration_start)
  {
    //Turn 1 motor on for x seconds until we feel confident the system is holding at the end stop
    //Set enc_count to the count it should be if we want 0 to be perfectly level

    //Set
    analogWrite(PWM_A, volts_to_PWM(0));
    analogWrite(PWM_B, volts_to_PWM(SUPPLY_VOLTAGE/2));

    //Hold motor for 5 seconds
    delay(5000);

    //Set enc_count to 94deg/2 
    enc_count = (PPR/360.0) * (94/2);

    //Shut off motors
    analogWrite(PWM_A, volts_to_PWM(0));
    analogWrite(PWM_B, volts_to_PWM(0));

    //Reset calibration flag to false
    com.calibration_start = false;
  }

  //Update Setpoint
  setpoint = com.setpoint;

  //Update Mode
  if (com.mode == 0) {
    motor_controller.SetMode(MANUAL);  // M0 - Controller Off, set motor output to zero
    motor_voltage = 0;
    base_motor_voltage=0;
  }
  else if (com.mode == 1) {
    motor_controller.SetMode(AUTOMATIC); // M1 - Controller On
    base_motor_voltage=2;
  }

  if (kp != com.kp || ki != com.ki || kd != com.kd) {
    kp = com.kp; ki = com.ki; kd = com.kd;  // Checking for difference before setting to prevent jitter
    motor_controller.SetTunings(kp, ki, kd); // Update gains
  }

  if (lowerOutputLimit != com.lowerOutputLimit || upperOutputLimit != com.upperOutputLimit) {
    lowerOutputLimit = com.lowerOutputLimit;
    upperOutputLimit = com.upperOutputLimit;
    motor_controller.SetOutputLimits(lowerOutputLimit, upperOutputLimit);
  }
  if (sampleTime != com.sampleTime) {
    sampleTime = com.sampleTime;
    motor_controller.SetSampleTime(sampleTime);
  }
}

//*****************************************************//
// Computes motor voltage based on appropriate labtypes
// Returns motor_vcaoltage
void compute_motor_voltage(int labtype) {
  switch (labtype) {
    case 0: // Angle Control
      motor_controller.Compute();
      if (motor_voltage < 0) {
        digitalWrite(DIR_B, LOW); // CCW
      }
      else {
        digitalWrite(DIR_B, LOW); // CW
      }
      analogWrite(PWM_A, volts_to_PWM(abs(base_motor_voltage - motor_voltage)));
      analogWrite(PWM_B, volts_to_PWM(abs(base_motor_voltage + motor_voltage)));
      
      break;

    case 1: // Speed Control
      motor_controller.Compute();
      analogWrite(PWM_B, volts_to_PWM(((0.0018 * com.setpoint) + motor_voltage)));
      break;

    case 2: // Open Loop Speed Control
      calc_motor_speed();
      if (com.mode == 1) {
        motor_voltage = com.open_loop_voltage;
      }
      else if (com.mode == 0) {
        motor_voltage = 0;
      }
      analogWrite(PWM_B, volts_to_PWM(motor_voltage));
      break;

    default: break; // Null default
  }
}

//*****************************************************//
void calc_motor_speed() {
  //  Check if motor is stationary
  //  if(micros() -  prev_pulse_time > stationary_thresh){
  //    motor_speed = 0;
  //  }
  //  else{
  //    motor_speed = update_motor_speed_array(motor_direction*double(360.0/PPR_A)*float(1000000.0/pulse_interval));
  //  }
  current_millis = micros();
  unsigned long dt = current_millis - prev_millis;
  if ( dt > DELTA_T)
  {
    //Calculate velocity
    motor_speed = (enc_deg - prev_pos) * double(1000000.0 / dt);
    prev_millis = current_millis;
    prev_pos = enc_deg;
  }
  //   Serial.println(motor_speed);
}

//*****************************************************//
// Update moving average speed array
double update_motor_speed_array(double newVal) {
  double sum = 0;
  for (int i = 0; i < MOVING_AVERAGE_SIZE - 1; i++) {
    motor_speed_array[i] = motor_speed_array[i + 1];
    sum += motor_speed_array[i];
  }
  motor_speed_array[MOVING_AVERAGE_SIZE - 1] = newVal;
  sum += newVal;
  return double(sum / MOVING_AVERAGE_SIZE);
}

//*****************************************************//
// Send data on request
void send_data() {
  // Check and if there is a request, send data
  if (com.write_data == 1) {
    Serial.print("T"); Serial.print(micros()); Serial.print(',');
    Serial.print('S'); Serial.print(setpoint); Serial.print(',');
    Serial.print('A');
    if (com.labType == 0) { // Angle
      Serial.print(enc_deg);
    }
    else if (com.labType == 1 || com.labType == 2) {
      Serial.print(motor_speed);
    }

    Serial.print(',');
    Serial.print('Q'); Serial.print(motor_voltage); Serial.print(',');
    // Serial.print('Q');Serial.print(volts_to_PWM(motor_voltage));Serial.print(',');
    Serial.println('\0');
    com.write_data = 0; // Reset write data flag
  }
}

//*****************************************************//
// Voltage and PWM duty cycle conversion
int volts_to_PWM(double voltage) {
  return constrain(round((voltage / SUPPLY_VOLTAGE) * 255), -255, 255);
}

double PWM_to_volts(int PWM) {
  return double(PWM / 255) * SUPPLY_VOLTAGE;
}

//*****************************************************//
//Encoder interrupts
void pulseA() {
  //  pulse_interval = micros() - prev_pulse_time;
  //  prev_pulse_time = micros();

  int valA = digitalRead(ENC_A);
  int valB = digitalRead(ENC_B);

  if (valA == HIGH) { // A Rise
    if (valB == LOW) {
      enc_count++;  // CW
      motor_direction = 1;
    }
    else {
      enc_count--;  // CCW
      motor_direction = -1;
    }
  }
  else { // A fall
    if (valB == HIGH) {
      enc_count ++;  // CW
      motor_direction = 1;
    }
    else {
      enc_count --;  //CCW
      motor_direction = -1;
    }
  }
}

void pulseB() {
  int valA = digitalRead(ENC_A);
  int valB = digitalRead(ENC_B);

  if (valB == HIGH) { // B rise
    if (valA == HIGH) {
      enc_count ++; // CW
    }
    else {
      enc_count --; // CCW
    }
  }
  else { //B fall
    if (valA == LOW) {
      enc_count ++; // CW
    }
    else {
      enc_count --; // CCW
    }
  }
}
