/*
CUatHomeLab.h

Jared Jacobowitz and YoungWoong Cho
Winter 2020

Function definitions for the abstract CUatHomeLab class. All labs will inherit
this class (and by extension the inherited super-class SerialComms). This class
outlines that each lab will have at least two functions: process_cmd and
run_lab. These are virtual functions which will be defined by each lab.
*/

#include "CUatHomeLab.h"
#include <Arduino.h>

CUatHomeLab::CUatHomeLab() {};

// First check if there are any change in: 1) lab type 2) sampling rate 3) sampling time
// Then reflect the changes and call process_cmd()
void CUatHomeLab::retrieve_cmd() {
	if (Serial.available()) {
		// Store a single command into the cmd_string array
		incoming_char = Serial.read();
		cmd_string[cmd_index] = incoming_char;
		// If end of the command, process the command
		if (incoming_char == '\0' || incoming_char == '%') {

			// First check if any parameter changed before running the lab
			// 1. Check if lab changed
			// 2. Check if sampling rate changed
			// 3. Check if sampling time changed
			new_lab_code = get_cmd_code('L', -1);
			if (get_cmd_code('S', -1) == 1){
				new_dt = get_cmd_code('A', -1);
				new_sample_time = get_cmd_code('B', -1);
			}
			// Reflect the changes
			if (new_lab_code != -1 && new_lab_code != lab_code) { lab_changed = true; }
			if (new_dt != -1 && new_dt != dt) { dt_changed = true; }
			if (new_sample_time != -1 && new_sample_time != sample_time) { sample_time_changed = true; }
			// If lab not changed
			else { process_cmd(); }
			//Reset the values used for retrieving the command
			cmd_index = 0;
			memset(cmd_string, '\0', sizeof(cmd_string)); // resets to all \0
		}
		// If not end of the command, proceed to the next char
		else { ++cmd_index; }
	}
}

double CUatHomeLab::get_cmd_code(char key, int def) {
	// Search string for first instance of key; return def if not found
	int cmd_start{ 0 };
	while (cmd_string[cmd_start]) {
		if (cmd_string[cmd_start] == key) {
			++cmd_start; // increment to get the index after the key
			break;
		}
		if (cmd_string[cmd_start + 1] == '\0' || cmd_string[cmd_start + 1] == '%') {
			return def;
		}
		++cmd_start;
	}

	// Find position of the comma or \0 to get the index of the end of the code.
	// % is for manual testing in the Arduino serial monitor.
	int cmd_end{ cmd_start };
	while (cmd_string[cmd_end] && !(cmd_string[cmd_end] == ',' || cmd_string[cmd_end] == '\0' || cmd_string[cmd_end] == '%')) {
		++cmd_end;
	}

	//Serial.print("Start: "); Serial.println(cmd_start);
	//Serial.print("End: "); Serial.println(cmd_end);
	char cmd[20];
	strncpy(cmd, &cmd_string[cmd_start], cmd_end - cmd_start);
	cmd[cmd_end - cmd_start] = '\0'; // dangerous if code is too long
	//Serial.print("cmd array: "); Serial.println(cmd);
	return atof(cmd); // return the substring in float format
}

void CUatHomeLab::process_cmd() {
	int cmd;
	cmd = get_cmd_code('R', -1);
	switch (cmd) {
	// When R0 command is sent
	case 0:
		// Turn is_logging_data false so that ardino will stop logging data
		is_logging_data = false;
		Serial.flush();
		break;
	
	
	// When R1 command is sent
	case 1:
		// Turn is_logging_data on so that arduino will begin logging data
		//is_logging_data = true;
		//is_sending_data = false;
		//is_sending_without_log_data = false;
		//logging_has_begun = false;
		//wrap = false;
		
		//send_index = 0;
        
        //init();

		time = 0;
		start_micros = micros();
		prev_micros = start_micros;
        log_index = 0;
        while (log_index < data_array_length){
            current_micros = micros();
            delta = current_micros - prev_micros;
            if (delta >= dt * 1000000){
                DAQ();
                log_index++;
                time += dt * 1000000;
                prev_micros = current_micros;
            }
        }
		break;
    case 2:
        send_index = 0;
        time = 0;
        start_micros = micros();
		prev_micros = start_micros;
		while (send_index < data_array_length){
            current_micros = micros();
            delta = current_micros - prev_micros;
            if (delta >= 0.0001 * 1000000){
                TSAQ();
                send_index++;
                time += dt * 1000000;
                prev_micros = current_micros;
            }
        }
        Serial.print('T'); Serial.print('#');
        Serial.print(',');
        Serial.print('S'); Serial.print('#');
        Serial.print(',');
        Serial.print('A'); Serial.print('#');
        Serial.print(',');
        Serial.print('Q'); Serial.println('#');
	default:
		break;
	}
}

// log_data method must take control of the follows:
// With the assumption: log_index increases faster than send_index does
// 1. keep logging data to the array as fast as possible
// 2. reset log_index to 0 the end of the array is reached
// 3. if log_index catches up send_index, stop logging while keep printing
void CUatHomeLab::log_data() {
	// Updates time variable
	current_micros = micros();
	delta = current_micros - prev_micros;
	// 1. Checks if logging is ready
	// if ALL:
	// 	a) dt has passed
	//	b) sample_time has not passed
	//	c) is_logging_data
    
	if (delta >= dt * 1000000 && log_index < data_array_length && is_logging_data){
		//logging_has_begun = true;

		DAQ();

		// If end of the array is reached, reset log_index to 0 and set wrap = true
		log_index++;
		//log_index %= data_array_length;
		//if (log_index == 0 && !wrap) { wrap = true; }

		time += dt * 1000000;
		prev_micros = current_micros;
	}
    else if (log_index >= data_array_length){
        is_logging_data = false;
        is_sending_data = true;
        send_index = 0;
    }
}

// send_data method must take control of the follows:
// With the assumption: log_index increases faster than send_index does
// 1. keep sending data to the serial as fast as possible
// 2. reset send_index to 0 the end of the array is reached
void CUatHomeLab::send_data() {
    //Serial.println(send_index); 
    if (is_sending_data && GUIreceived && send_index < data_array_length){
		// Whether or not is_logging_data is true, keep sending data to the serial
		TSAQ();
		// If end of the array is reached, reset print_index to 0
		send_index++;
		//GUIreceived = false;
	}
    else if (send_index >= data_array_length){
        is_sending_data = false;
        send_index = 0;
        log_index = 0;
    }
}

// send_without_log_data directly sends the serial to python as soon as stored
// This method is called when send_index increases faster than log_index does
void CUatHomeLab::send_without_log_data(){
	// Updates time variable
	current_micros = micros();
	delta = current_micros - prev_micros;
	if (delta >= dt * 1000000 && time <= sample_time * 1000000 && is_logging_data && is_sending_data){
		DAQ();
		TSAQ();
		// If end of the array is reached, reset the indices log_index and send_index to 0
		log_index++;
		log_index %= data_array_length;
		send_index %= data_array_length;

		time += dt * 1000000;
		prev_micros = current_micros;
	}
}

// log_send_coord checks if log_index = send_index
// and if so, either halts logging or sending data accordingly
void CUatHomeLab::log_send_coord() {
		// If this is the case, log_index has catched up send_index
		if ((is_logging_data || is_sending_data) && log_index == send_index && logging_has_begun){
			// 3-1. Checks if log_index has catched up send_index; if so, stop logging while keep printing
			if (wrap){ is_logging_data = false; wrap = false; }
			// 3-2. Checks if send_index has catched up log_index, but the data is still being logged(this implies that send_index is increasing faster than log_index does); if so, directly send what's being logged
			else if (is_logging_data == true) { is_sending_without_log_data = true; }//Serial.println("Changing to Sending w/o Log"); }
			// 3-3. Checks if send_index has catched up log_index, and data logging is already finished; if so, stop sending data since all is sent
			else if (is_logging_data == false) { is_sending_data = false; }
		}
}