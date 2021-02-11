/*
DefaultLab.h

YoungWoong Cho
Winter 2020

Function declerations for the Default Lab class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class is a default lab that will be instantiated when the default 
CUatHomeLab constructor is called.
*/

#ifndef DEFAULTLAB_H
#define DEFAULTLAB_H

#include "CUatHomeLab.h"
#include <Arduino.h>

class DefaultLab : public CUatHomeLab {
public:
	DefaultLab(int ARDUINO_BOARD_CODE);
	void DAQ();
	void TSAQ();
    //void init();
};

#endif // !DEFAULTLAB_H