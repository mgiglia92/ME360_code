/*
Statics.h

Jared Jacobowitz
Winter 2020

Function declerations for the Statics class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class contains also contains all the variables and functions necessary for
running the Statics lab using the CUatHome kit.
*/

#ifndef STATICS_H
#define STATICS_H

#include "CUatHomeLab.h"
#include <Arduino.h>

class Statics : public CUatHomeLab {
private:
	// Dynamically allocated arrays for data holding.
	// Need to be dynamic because the array size depends on the Arduino.
	float* analog0;
public:
	Statics(int ARDUINO_BOARD_CODE);
	~Statics();
	void DAQ();
	void TSAQ();
};

#endif // !STATICS_H