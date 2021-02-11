// Define hardware pins
#define ENC_A 2   //Encoder A
#define ENC_B 3   //Encoder B
#define PPR 211.2 //Encoder pulses per revolution 
#define PPR_A 52.8 //Pulse A per rev
#define DIR_B 13 //Motor Direction
#define PWM_B 11 //Motor PWM
#define BRK_B 8  //Motor Break


//Global Variables
double motor_rpm;
int enc_count,enc_count_memory;
double start_time;
double pulseA_ti, pulseA_tf, pulseA_time, pulse_interval;
int valA, valB;
char input;

void setup() {
  Serial.begin(9600);  // Begins Serial communication

  //Encoder Setup
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), pulseA, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_B), pulseB, CHANGE);
  
  //Motor Setup
  pinMode(PWM_B, OUTPUT);
  pinMode(DIR_B, OUTPUT);
  digitalWrite(PWM_B,LOW);  // Breaks Motor

  start_time = micros(); 
}

void loop(){
  input = Serial.read();
  calc_motor_rpm();
  if(input == 'A'){
    delay(500);
    digitalWrite(PWM_B,HIGH);
    Serial.println("Start motor");
  }
  else if(input == 'B'){
    Serial.print(millis());
    Serial.print(',');
    Serial.println(motor_rpm);
  }
  else if(input == 'C'){
    digitalWrite(PWM_B,LOW);
  }
}

void calc_motor_rpm(){
  if(pulseA_tf > pulseA_ti){
    pulse_interval = pulseA_tf - pulseA_ti;
    motor_rpm = double(1000000/(pulse_interval))/PPR_A*60.00;
  }
  else if(enc_count == enc_count_memory){
    motor_rpm = 0;
  }
}

//Encoder interrupts
void pulseA() {
  enc_count_memory = enc_count;
  pulseA_time = micros();
  valA = digitalRead(ENC_A);
  valB = digitalRead(ENC_B);
  
  if(valA == HIGH){  // A Rise 
    pulseA_ti = pulseA_time;
    if(valB == LOW){enc_count ++;}  // CW
    else{enc_count --;}  // CCW
  }
  else{  // A fall
    pulseA_tf = pulseA_time;
    if(valB == HIGH){enc_count ++;}  // CW
    else{enc_count --;}  //CCW
  }
}

void pulseB() {
  enc_count_memory = enc_count;
  valA = digitalRead(ENC_A);
  valB = digitalRead(ENC_B);
  
  if(valB == HIGH){  // B rise
    if(valA == HIGH){enc_count ++;}  // CW
    else{enc_count --;}  // CCW
  }
  else{  //B fall
    if(valA == LOW){enc_count ++;}  // CW
    else{enc_count --;}  // CCW
  }
}
