// Define hardware pins for Drone Control System
#define ENC_A 18   //Encoder pulse A
#define ENC_B 19   //Encoder pulse B
#define PPR 2400.0 //Encoder pulses per revolution 
#define PPR_A 232.8 //Pulse A per r
#define DIR_A 12
#define DIR_B 13 //Motor Direction HIGH = CW, LOW = CCW
#define PWM_A 3
#define PWM_B 11 //Motor PWM
#define BRK_B 8  //Motor Break Doesn't seem to work, avoid using
#define SUPPLY_VOLTAGE 9 //12V power supply
#define MOVING_AVERAGE_SIZE 50 // Size of moving average array