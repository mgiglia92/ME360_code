/*
SpeedofSound.h

Jared Jacobowitz and YoungWoong Cho
Winter 2020

Function declerations for the SpeedofSound class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class contains also contains all the variables and functions necessary for
running the Speed of Sound lab using the CUatHome kit.
*/

#ifndef SPEED_OF_SOUND_H
#define SPEED_OF_SOUND_H

#include "CUatHomeLab.h"
#include <Arduino.h>

class SpeedofSound : public CUatHomeLab {
private:
	// Dynamically allocated arrays for data holding.
	// Need to be dynamic because the array size depends on the Arduino.
	int* mic1;
	int* mic2;
    //int* times;
public:
	SpeedofSound(int ARDUINO_BOARD_CODE);
	~SpeedofSound();
	//void init();
    void DAQ();
	void TSAQ();
};

#endif // !SPEED_OF_SOUND_H