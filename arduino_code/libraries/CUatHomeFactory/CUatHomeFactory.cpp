/*
CUatHomeFactory.cpp

Jared Jacobowitz and YoungWoong Cho
Winter 2020

Function definitions for the CUatHomeFactory class. This class's sole purpose is
to create the proper lab when instantiated and then return that lab when called.

When adding a new lab to the CU@Home kit, the new lab must be added to the 
constructor switch statement and the header file must be included.
*/

#include "CUatHomeFactory.h"
#include "CUatHomeLab.h"

#include "DefaultLab.h"
#include "GeneralDAQ.h"
#include "Statics.h"
#include "SpeedofSound.h"
#include "Beam.h"

// Constructor instantiates a CUatHomeLab object according to the specified lab
// code. This object will be dynamically allocated as there is no way to know
// which lab will be run before it is specified by the Python "L" command.
CUatHomeFactory::CUatHomeFactory(int ARDUINO_BOARD_CODE) { lab = new DefaultLab(ARDUINO_BOARD_CODE); }

CUatHomeFactory::CUatHomeFactory(int lab_code, int ARDUINO_BOARD_CODE) {
	switch (lab_code) {
	case 1:
		lab = new GeneralDAQ(ARDUINO_BOARD_CODE);
		break;
	case 2:
		lab = new Statics(ARDUINO_BOARD_CODE);
		break;
	case 3:
		lab = new SpeedofSound(ARDUINO_BOARD_CODE);
		break;
	case 4:
		lab = new Beam(ARDUINO_BOARD_CODE);
		break;
	default:
		lab = nullptr;
		break;
	}
}

// Destructor called when changing the lab type (or the code finishes and the 
// object goes out of scope)
CUatHomeFactory::~CUatHomeFactory() {
	delete lab;
	lab = nullptr;
}

// lab is a pointer to the CUatHomeLab object, which will correspond to 
// instantiated lab type.
CUatHomeLab* CUatHomeFactory::get_lab() { return lab; }