/*
ProCon.cpp

Jared Jacobowitz and YoungWoong Cho
Winter 2020

Function definitions for the ProCon class. This class is a subclass of 
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class contains also contains all the variables and functions necessary for
running the ProCon lab using the CUatHome kit.
*/

#include "ProCon.h"
#include "CUatHomeLab.h"
#include "PID_beard.h"
#include "Differentiator.h"
#include "motor_control_hardware_config.h"
#include <Arduino.h>

int ProCon::enc_count = 0;

ProCon::ProCon() {
	//Encoder Setup
	pinMode(ENC_A, INPUT_PULLUP);
	pinMode(ENC_B, INPUT_PULLUP);

	attachInterrupt(digitalPinToInterrupt(ENC_A), pulseA, CHANGE);
	attachInterrupt(digitalPinToInterrupt(ENC_B), pulseB, CHANGE);

	//Motor Setup
	pinMode(PWM_B, OUTPUT);
	pinMode(DIR_B, OUTPUT);
	digitalWrite(PWM_B, LOW); // Stop Motor on Start Up
}

void ProCon::process_cmd() {
	//Serial.println("Calling ProCon process_cmd");
	int pos;
	int cmd;

	//Handshake command
	cmd = get_cmd_code('H', -1);
	switch (cmd) {
	case 0: // Handshake stuff to be implemented
		break;
	default: break;
	}

	//Request command
	cmd = get_cmd_code('R', -1);
	switch (cmd) {
	case 0: { //Flag to write data
		write_data = !write_data;
		//Serial.println("Write data on");
		//return;
	}
		break;

	//If no matches, break
	default: 
		break;
	}

	//Set value/mode commands
	cmd = get_cmd_code('S', -1);
	//Serial.print("S"); Serial.println(cmd);
	switch (cmd) {
	case 0: { //Set PID gains
		double new_kp = get_cmd_code('P', -1);
		if (new_kp != -1 && new_kp != kp) {
			kp = new_kp;
		}

		double new_ki = get_cmd_code('I', -1);
		if (new_ki != -1 && new_ki != ki) {
			ki = new_ki;
		}

		double new_kd = get_cmd_code('D', -1);
		if (new_kd != -1 && new_kd != kd) {
			kd = new_kd;
		}
		//Serial.print("P"); Serial.print(kp); 
		//Serial.print(" I"); Serial.print(ki);
		//Serial.print(" D"); Serial.println(kd);
	}
		break;

	case 1: { //Set Setpoint
		double new_setpoint = get_cmd_code('Z', -1);
		if (new_setpoint != -1 && new_setpoint != setpoint) {
			setpoint = new_setpoint;
		}
		//Serial.print("Setpoint: "); Serial.println(setpoint);
	}
		break;
	case 2: { //Set Lab type
		// 0: Position control
		// 1: Speed control
		// 2: OL?
		int new_labType{ get_cmd_code('Y', -1) };
		//Serial.print("old labType: "); Serial.println(labType);
		if (new_labType != -1 && new_labType != labType) {
			labType = new_labType;
		}
		//Serial.print("new labType: "); Serial.println(labType);
	}
		break;
	case 3: { //Set Controller Mode (on/off)
		int new_mode{ get_cmd_code('M', -1) };
		if (new_mode != -1 && new_mode != mode) {
			mode = new_mode;
		}
		//Serial.print("Mode: "); Serial.println(mode);
	}
		break;
	case 4: { //Set Sample Period
		double new_sample_period{ get_cmd_code('T', -1) };
		if (new_sample_period != -1 && new_sample_period != sample_period) {
			sample_period = new_sample_period;
			controller.update_time_parameters(sample_period, sigma);
			diff.update_time_parameters(sample_period, sigma);
		}
		//Serial.print("Sample Period: "); Serial.println(sample_period);
	}
		break;

	case 5: { //Set Output Limits
		double new_lowerOutputLimit{ get_cmd_code('L', -1) };
		if (new_lowerOutputLimit != -1 && new_lowerOutputLimit != lowerOutputLimit) {
			lowerOutputLimit = new_lowerOutputLimit;
		}

		double new_upperOutputLimit{ get_cmd_code('U', -1) };
		if (new_upperOutputLimit != -1 && new_upperOutputLimit != upperOutputLimit) {
			upperOutputLimit = new_upperOutputLimit;
		}
		//Serial.print("Lower Output Limit: "); Serial.println(lowerOutputLimit);
		//Serial.print("Upper Output Limit: "); Serial.println(upperOutputLimit);
	}
		break;
	case 6: { //Openloop control
		double new_open_loop_voltage{ get_cmd_code('O', 0) };
		if (new_open_loop_voltage != 0 && new_open_loop_voltage != open_loop_voltage) {
			open_loop_voltage = new_open_loop_voltage;
		}
	}
		break;
	case 7: { //Feed Foward Voltage
		double new_FF_A{ get_cmd_code('A', 0) };
		if (new_FF_A != 0 && new_FF_A != FF_A) {
			FF_A = new_FF_A;
		}
		double new_FF_B{ get_cmd_code('B', 0) };
		if (new_FF_B != 0 && new_FF_B != FF_B) {
			FF_B = new_FF_B;
		}
		double new_FF_C{ get_cmd_code('C', 0) };
		if (new_FF_C != 0 && new_FF_C != FF_C) {
			FF_C = new_FF_C;
		}
	}
		break;
	case 8: { //Open Loop Step Resonse Analysis
		open_loop_analysis_start = true;
		double new_open_loop_analysis_time{ get_cmd_code('T', -1) };
		if (new_open_loop_analysis_time != -1 && new_open_loop_analysis_time != open_loop_analysis_time) {
			open_loop_analysis_time = new_open_loop_analysis_time;
		}
	}
		break;
	case 9: {
		calibration_start = true;
	}
		break;
	case 10: {
		int new_anti_windup_activated{ get_cmd_code('W', -1) };
		if (new_anti_windup_activated != -1 && new_anti_windup_activated != anti_windup_activated) {
			anti_windup_activated = new_anti_windup_activated;
		}
	}
		break;
	default: 
		break;
	}
}

void ProCon::run_lab() {
	//Update Mode
	// M0 - Controller Off, set motor output to zero
	if (mode == 0) {
		controller_on = false;
		pid_output = 0;
	}
	// M1 - Controller On
	else if (mode == 1) {
		controller_on = true;
	}

	update_control_params();
	compute_motor_voltage();

	// Check and if there is a request, send data
	if (write_data) {
		Serial.print("T"); Serial.print(micros()); Serial.print(',');
		Serial.print('S'); Serial.print(setpoint); Serial.print(',');
		Serial.print('A');
		if (labType == 0) { // Angle
			Serial.print(enc_deg);
		}
		else if (labType == 1 || labType == 2) {  // Speed
			Serial.print(angular_velocity / RPM_TO_RADS);
		}

		Serial.print(',');
		Serial.print('Q'); Serial.print(pid_output); Serial.print(',');
		Serial.println('\0');
		write_data = false; // Reset write data flag
		//Serial.println("Write data off");
	}
}

void ProCon::update_control_params() {
	//Check for OpenLoop Analysis and run
	if (open_loop_analysis_start) {
		unsigned long init_time = millis();
		unsigned long current_time = init_time;
		unsigned long prev_time = init_time;

		//Set motor open loop voltage
		pid_output = open_loop_voltage;
		analogWrite(PWM_B, volts_to_PWM(pid_output));

		//Reset Open Loop differentiator
		enc_deg = count_to_deg(enc_count);
		diff.reset(enc_deg);

		int index{ 0 };
		while (index < storage_length - 1) {
			enc_deg = count_to_deg(enc_count); //Update encoder degrees
			current_time = millis();

			//NB: replace millis with micros
			if (current_time - prev_time >= (diff.Ts * 1000)) {
				time[index] = current_time - init_time;
				velocity[index] = diff.differentiate(enc_deg);
				prev_time = current_time;
				++index;
			}
		}
		open_loop_analysis_start = false;
		diff.update_time_parameters(diff.Ts, 0.01); //Reset differentiator sigma value
		diff.reset(count_to_deg(enc_count));

		//Send long serial data to python
		for (index = 0; index < storage_length - 1; ++index) {
			Serial.print("D0"); Serial.print(',');
			Serial.print('T'); Serial.print(time[index]); Serial.print(',');
			Serial.print('P'); Serial.print(0); Serial.print(',');
			Serial.print('V'); Serial.print(velocity[index] * DEGS_TO_RPM); Serial.print(',');
			Serial.print('I'); Serial.print(pid_output); Serial.print('$');
		}
		Serial.print('\n');
	}
}

void ProCon::compute_motor_voltage() {
	enc_deg = count_to_deg(enc_count); // Retrieve Current Position in Radians
	current_micros = micros(); //Get current microseconds

	switch (labType) {
	case 0: { // Angle Control
		if (controller_on && ((current_micros - prev_micros) >= (controller.Ts * 1000000.0))) {
			//If controller and sample period amount has passed, do processing
			//Calculate PID output
			pid_output = controller.PID(setpoint * DEG_TO_RAD, enc_deg * DEG_TO_RAD);
			//          Serial.print(" | dt: "); Serial.print(current_micros - prev_micros);
			//          Serial.print(" | setpoint: "); Serial.print(setpoint);
			//          Serial.print(" | encdeg: "); Serial.print(enc_deg);
			//          Serial.print(" | Ts: "); Serial.print(controller.Ts, 10);
			//          Serial.print(" | kp: "); Serial.print(controller.kp);
			//          Serial.print(" | beta: "); Serial.print(controller.beta);
			//          Serial.print(" | sigma: "); Serial.print(controller.sigma);
			//          Serial.print(" | pidout: ");
			//          Serial.println(pid_output);

						//update prev variables
			prev_micros = current_micros;
			prev_deg = enc_deg;
		}
		pid_output = pid_output_signal_conditioning(pid_output);
		update_motor_voltage(pid_output);
	}
		break;
	case 1: { // Speed Control
		//If sample period amount has passed do processing
		if ((current_micros - prev_micros) >= (controller.Ts * 1000000.0)) {
			//Calculate angular velocity from derivative
			angular_velocity = diff.differentiate(enc_deg * DEG_TO_RAD);
			//Calculate PID output
			pid_output = controller.PID(setpoint * RPM_TO_RADS, angular_velocity);
			//update prev variables
			prev_micros = current_micros;
			prev_deg = enc_deg;
		}
		if (controller_on) {
			pid_output = pid_output_signal_conditioning(pid_output);
			update_motor_voltage(pid_output);
		}
		else {
			analogWrite(PWM_B, 0);
		}
	}
		break;
	case 2: { // Open Loop Speed Control
		// Change motor voltage to open loop voltage if controller is on
		if (mode == 1) {
			pid_output = open_loop_voltage;
		}
		if ((current_micros - prev_micros) >= (controller.Ts * 1000000.0)) {
			//Calculate angular velocity from derivative
			angular_velocity = diff.differentiate(enc_deg * DEG_TO_RAD);
			//update prev variables
			prev_micros = current_micros;
			prev_deg = enc_deg;
		}
		analogWrite(PWM_B, volts_to_PWM(pid_output));
	}
		break;
	default: 
		break; // Null default
	}
}

void ProCon::update_motor_voltage(double voltage) {
	//Fix direction based on +/-
	if (voltage < 0) {
		digitalWrite(DIR_B, LOW); // CCW
	//    analogWrite(PWM_B, 0);
	//    return;
	}
	else {
		digitalWrite(DIR_B, HIGH); // CW
	}
	//set pwm based off of voltage
	analogWrite(PWM_B, volts_to_PWM(abs(voltage)));
}

int ProCon::volts_to_PWM(double voltage) {
	// Convert voltage to PWM duty cycle percent relative to the power supply voltage
	return constrain(round((voltage / SUPPLY_VOLTAGE) * 255), -255, 255);
}

double ProCon::PWM_to_volts(int PWM) {
	return double(PWM / 255) * SUPPLY_VOLTAGE;
}

double ProCon::pid_output_signal_conditioning(double val) {
	return constrain(val, lowerOutputLimit, upperOutputLimit);
}

double ProCon::count_to_deg(double count) {
	return (count / PPR) * 360.0;  // rad = (count / pulse/rev) * 360 deg/rev
}

static void ProCon::pulseA() {
	int valA = digitalRead(ENC_A);
	int valB = digitalRead(ENC_B);

	if (valA == HIGH) { // A Rise
		if (valB == LOW) {
			++enc_count;  // CW
		}
		else {
			--enc_count;  // CCW
		}
	}
	else { // A fall
		if (valB == HIGH) {
			++enc_count;  // CW
		}
		else {
			--enc_count;  //CCW
		}
	}
}

static void ProCon::pulseB() {
	int valA = digitalRead(ENC_A);
	int valB = digitalRead(ENC_B);

	if (valB == HIGH) { // B rise
		if (valA == HIGH) {
			++enc_count; // CW
		}
		else {
			--enc_count; // CCW
		}
	}
	else { //B fall
		if (valA == LOW) {
			++enc_count; // CW
		}
		else {
			--enc_count; // CCW
		}
	}
}