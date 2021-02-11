#include <Differentiator.h>
#include <motor_control_hardware_config.h>

unsigned long prev_micros = 0;
unsigned long current_micros;

volatile double enc_count;  //Encoder "ticks" counted, Enc ++ = CW, Enc -- = CCW
double enc_deg; // Encoder position in degrees
double prev_deg = 0;

double sigma = 0.1; //1/sigma = dirty derivative bandwidth (NB: why when this value is really small get lots of jumping)
double sample_period = 0.005; //in sec
Differentiator diff(sigma, sample_period);

void setup() {
  Serial.begin(500000);
  
  //Encoder Setup
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), pulseA, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_B), pulseB, CHANGE);
  
  digitalWrite(DIR_B, LOW); // CCW
  analogWrite(PWM_B, 150);
}

void loop() {
  enc_deg = count_to_deg(enc_count);
  current_micros = micros();
  
  if(((current_micros - prev_micros)) >= (diff.Ts * 1000000.0)){
    Serial.println(diff.differentiate(enc_deg*2*3.14159/360));
//    Serial.print(" | delta_deg: "); Serial.print(enc_deg - prev_deg);
//    Serial.print(" | time: "); Serial.println(current_micros - prev_micros);
    prev_micros = current_micros;
    prev_deg = enc_deg;
  }


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
