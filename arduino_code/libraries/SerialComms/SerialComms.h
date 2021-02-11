#include <Arduino.h>

class SerialComms{
public:
    //Process a command received from serial buffer
    void process_command(char*);
    //Search cmd for letter, return number immideately after letter
    double parse_number(char*, char, int);
    // SerialComms(int*, double*, pwmAngle, pwmVelocity, time);
    SerialComms();

    void handle_command();
    void send_data();

    //-------
    //Serial communication buffer params
    char cmd [200]; //Input command from serial
    int cmd_index; //Current index in cmd[] 
    char incoming_char; //Serial incoming character for "parallel processing" of serial data

    //Writing data variables
    int daq_out_index; //index showing last position of data that was sent
    int write_data;

    //--------------------------
    //Local variables to hold data from serial stream
    double dt; //time between samples
    double N; //Number of samples for recording
    int record_delay;
    bool delay_complete;
    
    unsigned int *mic1;
    unsigned int *mic2;
    unsigned int temp;
    int arr_length;//maximum length of array
    int start_reading; //flag to start recording data
    };


/*
Serial command protocol
-----------
Python -> Arduino

H0 - Handshake
R0 - Request one line of data
R1 - Request to start recording

S0,N#,% - Set N (num samples)
S1,T#% - Set dt
S2,T# - Set pre-record delay

Arduino -> Pyhon
T# - time in micros
A# - value of mic1
B# - value of mic2
C# - temperature
*/

// S0,P0.1,I0,D0,%
// S1,Z100,%
// S2,Y0,%
// S3,M1,%
// S4,T0.005,%
// S5,L-12,U12,%