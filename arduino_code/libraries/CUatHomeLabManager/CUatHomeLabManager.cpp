/*
CUatHomeLabManager.cpp

YoungWoong Cho
Winter 2020

Function definitions for the CUatHomeLabManager class. This class manages the 
creation and the destruction of the lab instances.
*/

#include <Arduino.h>
#include "CUatHomeLabManager.h"

CUatHomeLabManager::CUatHomeLabManager(int ARDUINO_BOARD_CODE) {
	ARDUINO_CODE = ARDUINO_BOARD_CODE;
	factory = new CUatHomeFactory(ARDUINO_CODE);
	lab = factory->get_lab();
}
void CUatHomeLabManager::run(){
	// Retrieve the command to check if there are any change in: 1) lab type 2) sampling rate 3) sampling time
    // After reflecting the changes, process_cmd() to either receive R0 or R1
    lab->retrieve_cmd();

	// If lab changed, destroy the old lab and create the new lab instance
    if (lab->lab_changed) { 
        int temp_lab_code{ lab->new_lab_code };

        factory->~CUatHomeFactory();
        lab->~CUatHomeLab();
        factory = new CUatHomeFactory(temp_lab_code, ARDUINO_CODE);
        lab = factory->get_lab();
        lab->lab_code = temp_lab_code;
    }
    if (lab->dt_changed) { lab->dt = lab->new_dt; lab->dt_changed = false; }
    if (lab->sample_time_changed) { lab->sample_time = lab->new_sample_time; lab->sample_time_changed = false; }

    // If lab is sending without logging data, directly send without logging data
    // if (lab->is_sending_without_log_data) { lab->send_without_log_data(); }
    // else {
    //     // If lab is logging data, log data. This process is done separately from send_data() process, which sends data to GUI
    //     if (lab->is_logging_data){ lab->log_data(); }
    //     lab->log_send_coord();
    // }
    if (lab->is_logging_data){ lab->log_data(); }
    if (lab->is_sending_data){ lab->send_data(); }
    lab->log_send_coord();
}