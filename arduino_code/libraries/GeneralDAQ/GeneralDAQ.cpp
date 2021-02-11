/*
GeneralDAQ.h

YoungWoong Cho
Winter 2020

Function definitions for the GeneralDAQ class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class contains also contains all the variables and functions necessary for
running the GeneralDAQ lab using the CUatHome kit.
*/

#include "GeneralDAQ.h"
#include "CUatHomeLab.h"
#include <Arduino.h>


GeneralDAQ::GeneralDAQ(int ARDUINO_BOARD_CODE) {
	lab_code = 1;
	ARDUINO_CODE = ARDUINO_BOARD_CODE;

	if (ARDUINO_CODE == 0) data_array_length = 500;
	else if (ARDUINO_CODE == 1) data_array_length = 50;

	analog0 = new double[data_array_length];
	analog1 = new double[data_array_length];
	analog2 = new double[data_array_length];
	analog3 = new double[data_array_length];
	analog4 = new double[data_array_length];
}

GeneralDAQ::~GeneralDAQ(){
	delete[] analog0;
	delete[] analog1;
	delete[] analog2;
	delete[] analog3;
	delete[] analog4;
}

void GeneralDAQ::DAQ() {
	analog0[log_index] = analogRead(A0);
	analog1[log_index] = analogRead(A1);
	analog2[log_index] = analogRead(A2);
	analog3[log_index] = analogRead(A3);
	analog4[log_index] = analogRead(A4);
}

void GeneralDAQ::TSAQ() {
	Serial.print('T'); Serial.print(time);
	Serial.print(',');
	Serial.print("S"); Serial.print(log_index);
	Serial.print(',');
	Serial.print("A"); Serial.print(send_index);
	Serial.print(',');
	Serial.print("Q"); Serial.print(is_sending_without_log_data	);
	// Serial.print(',');
	// Serial.print("A3: "); Serial.print(analog3[send_index]);
	// Serial.print(',');
	// Serial.print("A4: "); Serial.print(analog4[send_index]);
	Serial.print('\n');
}