#include <SerialComms.h>
#include <string.h>
#include <Arduino.h>

SerialComms::SerialComms(){
    //Initialize Serial buffer params
    cmd_index=0; //current index in cmd[]
    N = 1000; //Default num samples to 1000

    dt = 0.001; //time between samples (in seconds)
    arr_length=1000; //Maximum length of the mic data array
    daq_out_index=0;    //Index showing the last position of data that has been sent
    mic1 = new unsigned int[arr_length];
    mic2 = new unsigned int[arr_length];
    start_reading=0;//initialize to not start reading
    record_delay=0; //initialize record delay to 0 seconds
    write_data=0;
    delay_complete=false;
}

void SerialComms::process_command(char* cmd_string){
    int pos;
    int cmd;

    //Handshake command
    cmd = parse_number(cmd_string, 'H', -1);
    switch((int)(cmd)){
        case 0: // Handshake stuff to be implemented
            break;
        default: break;
    }

    //Request command
    cmd = parse_number(cmd_string, 'R', -1);
    switch((int)(cmd)){
        case 0: //Flag to write data
            write_data = 1;
            break;
        case 1: // Flag to start reading data, reset delay_complete
            start_reading = true;
            delay_complete=false;

        //If no matches, break
        default: break;
    }

    //Set value/mode commands
    cmd = parse_number(cmd_string, 'S', -1);
    switch(int(cmd)){
        case 0: //Set N (number of samples)
            N = (int)(parse_number(cmd_string, 'N', -1));
            break;

        case 1://Set dt
            fs = (float)(parse_number(cmd_string, 'T' , -1));
            dt = 1.0/fs;
            break;

        case 2: //Set pre-record delay
            record_delay = (int)(parse_number(cmd_string, 'T', -1));
            break;

        default: break;
    }
}

double SerialComms::parse_number(char* cmd_string, char key, int def){
    //Search cmd_string for key, return the number between key and delimiter
    // Serial.println(cmd_string);
    // Serial.println(key);

    int key_len=0; //Position of key in string
    int delim_len=0; //Position of next delimiter after key in string

    //Search string for first instance of key, increment key length each time key isn't found
    for(int i=0; i<100; i++) //TODO: Make this 100 value a HEADER_LENGTH #define
    {
        if(cmd_string[i] == '\0') { return def; } //If we can't find key, return default value
        if(cmd_string[i] == key){key_len = i; break;}
    }
    // Serial.print("key len: "); Serial.println(key_len);

    //Search string starting at character after key, looking for next delimiter the comma
    for(int i=key_len+1; i<100; i++){
        if(cmd_string[i] == ',' || cmd_string[i] == '\0')
        {
            break;
        }
        delim_len++;
    }
    // Serial.print("delim len: "); Serial.println(delim_len);

    //Create empty substring to use strncpy
    char substring[20] = {0};
    strncpy(substring, &cmd_string[key_len+1], delim_len);  //Copy subset of string to substring
    
    // Serial.print("test string: "); Serial.println(substring);
    return atof(substring); //return the substring in float format
}

void SerialComms::handle_command(){
// Arduino command handler
  if (Serial.available() != 0) {
    incoming_char = Serial.read();
    cmd[cmd_index] = incoming_char;
    if (incoming_char == '\0' || incoming_char == '%') {
      //      Serial.println("End of line, processing commands!");
      process_command(cmd);
      // Reset command buffer
      cmd_index = 0;
      memset(cmd, '\0', sizeof(cmd));
    }
    else {
      cmd_index ++;
    }
  }
}


void SerialComms::send_data()
{
    if(write_data) {
    Serial.print("T"); Serial.print(dt*daq_out_index,7); Serial.print(',');
    Serial.print('A'); Serial.print(mic1[daq_out_index]); Serial.print(',');

    Serial.print('B'); Serial.print(mic2[daq_out_index]); Serial.print(',');
    
    Serial.print('C'); Serial.print(fs); Serial.print(',');

    
    write_data = 0; // Reset write data flag
    daq_out_index++;
    //Check if we're at the end of the data array, print end of message character
    if(daq_out_index >= N) { daq_out_index = 0; Serial.print('#');} 
    Serial.print('\0');//print end of line character
  }
}