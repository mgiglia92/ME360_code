// If you're using an Arduino Teensy, uncomment the first line and comment the second.
// If you're using an Arduino Uno, comment the first line and uncomment the second.
// TEENSY = 0, UNO = 1
//int ARDUINO_BOARD_CODE{ 0 };
int ARDUINO_BOARD_CODE{ 1 };

#include "CUatHomeLabManager.h"

// DefaultLab = 0, GeneralDAQ = 1, Statics = 2, Speed of Sound = 3, Beam = 4
CUatHomeLabManager *labMgr = new CUatHomeLabManager(ARDUINO_BOARD_CODE);

void setup() { Serial.begin(1000000); }

void loop() { labMgr->run(); }
