/*
Beam.cpp

YoungWoong Cho
Winter 2020

Function definitions for the Beam class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class contains also contains all the variables and functions necessary for
running the Beam lab using the CUatHome kit.
*/

#include "Beam.h"
#include "CUatHomeLab.h"
#include <Arduino.h>

Beam::Beam(int ARDUINO_BOARD_CODE) {
	lab_code = 4;
	ARDUINO_CODE = ARDUINO_BOARD_CODE;

	if (ARDUINO_CODE == 0) data_array_length = 500;
	else if (ARDUINO_CODE == 1) data_array_length = 100;

	Wire.begin();
	mpu6050->begin();
	angAccX = new float[data_array_length];
}

Beam::~Beam() {
	delete[] angAccX;
}

void Beam::DAQ(){
	mpu6050->update();
	angAccX[log_index] = mpu6050->getAccAngleX();
}

void Beam::TSAQ() {
	Serial.print('T'); Serial.print(time);
	Serial.print(',');
	Serial.print('S'); Serial.print(angAccX[send_index]);
	Serial.print(',');
	Serial.print('A'); Serial.println(is_sending_without_log_data);
}