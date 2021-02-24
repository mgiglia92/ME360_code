#include <Differentiator.h>
#include <motor_control_hardware_config.h>

#define DEG_TO_RAD 2*3.14159/360
#define RPM_TO_RADS 0.104719755
#define DEGS_TO_RPM 0.166667

//Timing Parameters for fixed interval calculations for PID and derivitave
unsigned long prev_micros = 0;
unsigned long current_micros;

volatile double enc_count;  //Encoder "ticks" counted, Enc ++ = CW, Enc -- = CCW
double enc_deg; // Encoder position in degrees
double angular_velocity; //Angular velocity of the motor
double prev_deg =0; //Previous encoder position for angular velocity calculation
double sigma = 0.01; //Cutoff freq for band-limited derivative

double sample_period = 0.005;

Differentiator diff(sigma, sample_period);

//***********************************************************************************
void setup() {
  Serial.begin(500000);  // Begins Serial communication

  //Encoder Setup
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), pulseA, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_B), pulseB, CHANGE);

  //Initialize variables
  current_micros = micros();
  prev_micros = current_micros;
  prev_deg = 0;

}

//***********************************************************************************
void loop() {
   compute_motor_voltage(); // Update controller input, compute motor voltage and write to motor
   Serial.println(angular_velocity);
}

//*****************************************************//
// Computes and executes motor voltage based on appropriate labtypes
void compute_motor_voltage() {
  enc_deg = count_to_deg(enc_count); // Retrieve Current Position in Radians
  current_micros = micros(); //Get current microseconds

  if((current_micros - prev_micros) >= (diff.Ts * 1000000.0))
  {
    //Calculate angular velocity
    angular_velocity = diff.differentiate(enc_deg*DEG_TO_RAD);

    //update prev variables
    prev_micros = current_micros;
    prev_deg = enc_deg;
  }
}
//*****************************************************//

//Encoder Count to Radians
double count_to_deg(double count){
  return (double(count / PPR) * 360);  // rad = (count / pulse/rev) * 360 deg/rev
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
