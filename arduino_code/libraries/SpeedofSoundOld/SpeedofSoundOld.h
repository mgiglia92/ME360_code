/*
SpeedofSound.h

Jared Jacobowitz
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
	int mic1;
	int mic2;
	float t = 0;
public:
	SpeedofSound();
	void process_cmd();
	void run_lab();
};

#endif // !SPEED_OF_SOUND_H