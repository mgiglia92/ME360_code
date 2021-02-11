// Define hardware pins for Motor Control system
#define ENC_A 2   //Encoder pulse A
#define ENC_B 3   //Encoder pulse B
#define PPR 464.64 //Encoder pulses per revolution 
#define PPR_A 232.8 //Pulse A per r
#define DIR_B 13 //Motor Direction HIGH = CW, LOW = CCW
#define PWM_B 11 //Motor PWM
#define BRK_B 8  //Motor Break Doesn't seem to work, avoid using
#define SUPPLY_VOLTAGE 12 //12V power supply
#define MOVING_AVERAGE_SIZE 50 // Size of moving average 