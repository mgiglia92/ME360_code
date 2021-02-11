#include <PID_beard.h>
#include <motor_control_hardware_config.h>
#define DEG_TO_RAD 2*3.14159/360

//instantiate PID controller
double kp = 50;
double ki = 0;
double kd = 2;
double limit = 12;
double sigma = 0.05;
double sample_period = 0.005; //sample period in s
bool flag = true;

PIDControl controller(kp, ki, kd, limit, sigma, sample_period, flag);

//Other variables
volatile double enc_count;  //Encoder "ticks" counted, Enc ++ = CW, Enc -- = CCW
double enc_deg; // Encoder position in degrees
double angular_velocity; //Angular velocity of the motor
double prev_deg; //Previous encoder position for angular velocity calculation

unsigned long prev_micros, current_micros;

double setpoint = 100;
double pid_output;

void setup() {

  //Begin serial for debugging
  Serial.begin(500000);
  
  //Encoder Setup
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), pulseA, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_B), pulseB, CHANGE);
}

//counter variable
int counter = 1;

void loop() {

  
  //Update variables
  enc_deg = count_to_deg(enc_count);
  current_micros = micros(); //Get current microseconds

  //Flip setpoint after 3 seconds
  if((counter%1000)==0) { setpoint = -1*setpoint; }
  counter++;
  
  if(((current_micros - prev_micros)) >= (controller.Ts * 1000000.0))
  {          
    //Calculate PID output
    pid_output = controller.PID(setpoint*DEG_TO_RAD, enc_deg*DEG_TO_RAD);
    Serial.print("setpoint: "); Serial.print(setpoint);
    Serial.print(" | encdeg: "); Serial.print(enc_deg);
    Serial.print(" | Ts: "); Serial.print(current_micros - prev_micros, 10);
    Serial.print(" | kp: "); Serial.print(controller.kp);
    Serial.print(" | beta: "); Serial.print(controller.beta);
    Serial.print(" | sigma: "); Serial.print(controller.sigma);
    Serial.print(" | pidout: ");
    Serial.println(pid_output);
    
    //update prev variables
    prev_micros = current_micros;
    prev_deg = enc_deg;
  }
        



  //Update motor control values
  update_motor_voltage(pid_output);

  //Serial print for debugging
//  Serial.println(pid_output);
}

//Encoder interrupts
void pulseA(){
  int valA = digitalRead(ENC_A);
  int valB = digitalRead(ENC_B);

  if (valA == HIGH) { // A Rise
    if (valB == LOW) {
      enc_count++;  // CW
    }
    else {
      enc_count--;  // CCW
    }
  }
  else { // A fall
    if (valB == HIGH) {
      enc_count ++;  // CW
    }
    else {
      enc_count --;  //CCW
    }
  }
}

void pulseB(){
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

//*****************************************************//
// Voltage and PWM duty cycle conversion
int volts_to_PWM(double voltage) {
  return constrain(round((voltage / SUPPLY_VOLTAGE) * 255), -255, 255);
}

double PWM_to_volts(int PWM) {
  return double(PWM / 255) * SUPPLY_VOLTAGE;
}

//*****************************************************//

//Encoder Count to Radians
double count_to_deg(double count){
  return (double(count / PPR) * 360);  // rad = (count / pulse/rev) * 360 deg/rev
}

void update_motor_voltage(double voltage){
  //Fix direction based on +/-
  if (voltage < 0) {
    digitalWrite(DIR_B, LOW); // CCW
    } 
    
  else {
    digitalWrite(DIR_B, HIGH); // CW
  }
  //set pwm based off of voltage
  analogWrite(PWM_B, volts_to_PWM(abs(voltage)));
}
