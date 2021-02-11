/*
CUatHomeFactory.h

Jared Jacobowitz and YoungWoong Cho
Winter 2020

Function declerations for the CUatHomeFactory class. This class's sole purpose 
is to create the proper lab when instantiated and then return that lab when 
called.

When adding a new lab to the CU@Home kit, the new lab must be added to the
constructor switch statement and the header file must be included.
*/

#ifndef CU_AT_HOME_FACTORY_H
#define CU_AT_HOME_FACTORY_H

#include "CUatHomeLab.h"

class CUatHomeFactory {
public:
	// Constructor instantiates a CUatHomeLab object according to the specified 
	// lab code. This object will be dynamically allocated as there is no way to 
	// know which lab will be run before it is specified by the Python "L" 
	// command.
	// ARDUINO_CODE: TEENSY = 0, UNO = 1
	CUatHomeFactory(int ARDUINO_BOARD_CODE);

	CUatHomeFactory(int lab_code, int ARDUINO_BOARD_CODE);

	// Destructor called when changing the lab type (or the code finishes and 
	// the object goes out of scope)
	~CUatHomeFactory();

	// lab is a pointer to the CUatHomeLab object, which will correspond to 
	// instantiated lab type.
	CUatHomeLab* get_lab();
private:
	CUatHomeLab* lab{ nullptr };
};

#endif // !CU_AT_HOME_FACTORY_H