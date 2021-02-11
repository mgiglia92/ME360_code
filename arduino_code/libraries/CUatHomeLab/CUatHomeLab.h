/*
CUatHomeLab.h

Jared Jacobowitz and YoungWoong Cho
Winter 2020

Function declerations for the abstract CUatHomeLab class. All labs will inherit 
this class (and by extension the inherited super-class SerialComms). This class 
outlines that each lab will have at least two functions: process_cmd and 
run_lab. These are virtual functions which will be defined by each lab.
*/

#ifndef CU_AT_HOME_H
#define CU_AT_HOME_H

#include <Arduino.h>

class CUatHomeLab {
public:
	/*** Lab ***/
	/* 1)	Lab-type */
	int ARDUINO_CODE;  // 0:TEENSY, 1:UNO
	int lab_code; // Current lab code
	int new_lab_code; // New lab code
	bool lab_changed{ false };  // Will become true when new_lab command
	int data_array_length{ 0 };  // board-type dependent

	/* 2)	For sampling */
	unsigned long current_micros{ 0 };
	unsigned long prev_micros{ 0 };
	unsigned long start_micros{ 0 };
	double time{ 0 }; // Sampling time [s]; Time between data points will be approximately constant so this variable will just be incremented each print
	double dt{ 0.01 }; // Sampling time interval [s]
	double new_dt{ 0.01 }; // New sampling time interval
	bool dt_changed{ false }; // Will become true when new_dt command
	double sample_time{ 100 }; // Total sample time [s]
	double new_sample_time{ 100 }; // New sample time [s]
	bool sample_time_changed{ false }; // Will become true when new_sample_time command
	unsigned long delta; // Time passed since last prev_micros is logged [s]
	
	/*** Serial communication ***/
	/* 1)	For command retrieval */
	static const int storage_length{ 200 };
	char cmd_string[storage_length];
	int cmd_index{ 0 };
	char incoming_char;
	bool cmd_retrieved{ false };

	/* 2)	Reads a single command
			Called by lab to retrieve command string */
	void retrieve_cmd();

	/* 3)	Search cmd_string for the number after the specifiec key
			Returns the number immediately after key if it exists, def otherwise */
	double get_cmd_code(char key, int def);


	/* 4)	This function will look for specific command codes and
			then calling the proper functions. */
	void process_cmd();
    
	/* 5)	For data logging */
    //virtual void init() = 0;
	void log_data(); // This function is called each loop in the arduino code to log the data
	virtual void DAQ() = 0; // This function is what does the actual DAQ, which is lab-dependent
	bool is_logging_data{ false }; // true when logging data. Will become false when 1) log_index catches up send_index 2) STOP button pressed
	int log_index; // index that will be logged to the array
	bool wrap{ false };  // true when the log_index loops back to 0
	bool logging_has_begun{ false }; // true when at least one data log is completed. This prevents send_data from going ahead of log_data

	/* 6)	For data sending */
	void send_data(); // This function is called when R1 command is sent from GUI to send the data.
	virtual void TSAQ() = 0; // In this function is defined what is to be sent according to the TSAQ format, which is lab-dependent
	bool is_sending_data{ false }; // true when sending data. Will become false when logging is done and send_index catches up log_index
	int send_index; // index that will be sent to the serial
	bool GUIreceived{ false };

	/* 7) For sending data without logging */
	void send_without_log_data();
	bool is_sending_without_log_data{ false };

	/* 8) For log-send coordination */
	void log_send_coord();

	CUatHomeLab();
};

#endif // !CU_AT_HOME_H