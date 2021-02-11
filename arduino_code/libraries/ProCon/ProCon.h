/*
ProCon.h

Jared Jacobowitz and YoungWoong Cho
Winter 2020

Function declerations for the ProCon class. This class is a subclass of
CUatHomeLab and therefore must implement the process_cmd and run_lab functions.
This class contains also contains all the variables and functions necessary for
running the ProCon lab using the CUatHome kit.
*/

#ifndef PROCON_H
#define PROCON_H

//constexpr auto DEG_TO_RAD{ 2 * 3.14159 / 360 }; // defined in Arduino.h
constexpr auto RPM_TO_RADS{ 0.104719755 };
constexpr auto DEGS_TO_RPM{ 0.166667 };


#include "CUatHomeLab.h"
#include "PID_beard.h"
#include "Differentiator.h"
#include "motor_control_hardware_config.h"
#include <Arduino.h>

class ProCon : public CUatHomeLab {
private:
	double kp{ 5 };
	double ki{ 0 };
	double kd{ 1 };

	double setpoint{ 100 };

	double prev_deg{ 0 };
	double lowerLimit{ -1 * SUPPLY_VOLTAGE };
	double upperLimit{ SUPPLY_VOLTAGE };


	int lowerOutputLimit;
	int upperOutputLimit;

	bool write_data{ false };
	char data[200];

	int open_loop_voltage;

	double feed_forward_voltage;
	double FF_A;
	double FF_B;
	double FF_C;

	bool open_loop_analysis_start{ false };
	double open_loop_analysis_time;

	bool calibration_start;
	int anti_windup_activated;

	int mode{ 0 };
	int labType{ -1 };

	double pid_output{ 0 };
	bool controller_on{ false };

	unsigned long current_micros{ micros() };
	unsigned long prev_micros{ current_micros };

	double enc_deg{ 0 };

	double angular_velocity;

	// storage_length was defined in SerialComms
	int time[storage_length];
	int velocity[storage_length];

	// sample_period defined in SerialComms
	double sigma{ 0.01 };
	Differentiator diff{ sigma, sample_period };
	bool flag{ true };
	PIDControl controller{ kp, ki, kd, lowerLimit, upperLimit, sigma, sample_period, flag };

public:
	ProCon();
	void process_cmd();
	void run_lab();

	static int enc_count;

	void update_control_params();
	void compute_motor_voltage();
	void update_motor_voltage(double voltage);
	int volts_to_PWM(double voltage);
	double PWM_to_volts(int PWM);
	double pid_output_signal_conditioning(double val);
	double count_to_deg(double count);
	static void pulseA();
	static void pulseB();
};

#endif // !PROCON_H