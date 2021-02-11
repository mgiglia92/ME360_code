/*
SpeedofSound.cpp

Jared Jacobowitz
Winter 2020

Function definitions for the SpeedofSound class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class contains also contains all the variables and functions necessary for
running the Speed of Sound lab using the CUatHome kit.
*/

#include "SpeedofSound.h"
#include "CUatHomeLab.h"
#include <Arduino.h>


SpeedofSound::SpeedofSound() {}

void SpeedofSound::process_cmd() {
	int cmd;

	cmd = get_cmd_code('R', -1);
	switch (cmd) {
	case 0: // toggle data writing off
		write_data = false;
		break;
	case 1: // toggle data writing on
		if (!write_data) {
			write_data = true;
			start_micros = micros();
			prev_micros = start_micros;
		}
		break;
	default:
		break;
	}
}

void SpeedofSound::run_lab() {
	current_micros = micros();
	delta = current_micros - prev_micros;
	if (write_data && delta >= dt * 1000000) {
		t += 0.1;
		float sine = 10*sin(t);
		float cosine = 10*cos(t);

		Serial.print('T'); Serial.print(current_micros - start_micros);
		Serial.print(',');
		Serial.print('S'); Serial.print(3);
		Serial.print(',');
		Serial.print('A'); Serial.print(sine);
		Serial.print(',');
		Serial.print('Q'); Serial.println(cosine);
		prev_micros = current_micros;
		
		
		/*
		Serial.print('T'); Serial.print(current_micros - start_micros);
		Serial.print(',');
		Serial.print('S'); Serial.print(100);
		Serial.print(',');
		Serial.print('A'); Serial.print(analogRead(A0));
		Serial.print(',');
		Serial.print('Q'); Serial.println(analogRead(A0));
		prev_micros = current_micros;
		*/
		
	}
}