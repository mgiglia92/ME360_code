/*
Statics.cpp

Jared Jacobowitz
Winter 2020

Function definitions for the Statics class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class contains also contains all the variables and functions necessary for
running the Statics lab using the CUatHome kit.
*/

#include "Statics.h"
#include "CUatHomeLab.h"
#include <Arduino.h>

Statics::Statics(int ARDUINO_BOARD_CODE) {
	lab_code = 1;
	ARDUINO_CODE = ARDUINO_BOARD_CODE;

	if (ARDUINO_CODE == 0) data_array_length = 500;
	else if (ARDUINO_CODE == 1) data_array_length = 250;

	analog0 = new float[data_array_length];
}

Statics::~Statics(){
	delete[] analog0;
}

void Statics::DAQ() {
	analog0[log_index] = analogRead(A0);
}

void Statics::TSAQ() {
	int val = 0;
	if (is_sending_without_log_data) {val = 1;}
	Serial.print('T'); Serial.print(time);
	Serial.print(',');
	Serial.print("S"); Serial.print(log_index);
	Serial.print(',');
	Serial.print("A"); Serial.print(send_index);
	Serial.print(',');
	Serial.print("Q"); Serial.println(val);
}