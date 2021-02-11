/*
DefaultLab.h

YoungWoong Cho
Winter 2020

Function definitions for the DefaultLab class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class is a default lab that will be instantiated when the default 
CUatHomeLab constructor is called.
*/

#include "DefaultLab.h"
#include "CUatHomeLab.h"
#include <Arduino.h>


DefaultLab::DefaultLab(int ARDUINO_BOARD_CODE) { 
	ARDUINO_CODE = ARDUINO_BOARD_CODE;
	lab_code = 0; 
}

//void DefaultLab::init() {return;}

void DefaultLab::DAQ() {return;}

void DefaultLab::TSAQ() {return;}