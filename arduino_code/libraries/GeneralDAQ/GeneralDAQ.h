/*
GeneralDAQ.h

YoungWoong Cho
Winter 2020

Function declerations for the GeneralDAQ class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class contains also contains all the variables and functions necessary for
running the GeneralDAQ lab using the CUatHome kit.
*/

#ifndef GENERALDAQ_H
#define GENERALDAQ_H

#include "CUatHomeLab.h"
#include <Arduino.h>

class GeneralDAQ : public CUatHomeLab {
private:
	double* analog0;
	double* analog1;
	double* analog2;
	double* analog3;
	double* analog4;
public:
	GeneralDAQ(int ARDUINO_BOARD_CODE);
	~GeneralDAQ();
	void DAQ();
	void TSAQ();
};

#endif // !GENERALDAQ_H