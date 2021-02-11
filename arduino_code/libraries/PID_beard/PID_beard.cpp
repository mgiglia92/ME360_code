#include <PID_beard.h>
#include <Arduino.h>

//Constructor logic
PIDControl::PIDControl(double p, double i, double d, double llim, double ulim, double sigm, double t, bool fl){

    kp = p;
    ki = i;
    kd = d;
    lowerLimit = llim;
    upperLimit = ulim;
    sigma = sigm;
    Ts = t;
    flag = fl;
    beta = (2.0*sigma - Ts) / (2.0*sigma + Ts);

    //Initialize delayed values to zero
    y_d1 = 0;
    error_d1 = 0;

    //Initialize derivative values to zero
    y_dot = 0;
    error_dot = 0;

    //Initialize integrator value to zero
    integrator = 0;
}


//PID calculation
double PIDControl::PID(double y_r, double y){
    //Initialize variables to prevent compiler errors
    double u_unsat;

    //Compute the current error
    double error = y_r - y;

    //Integrate errkor using trapazoidal rule
    integrator = integrator + ((Ts/2) * (error + error_d1));

    if(anti_windup_activated==1 && ki != 0){
        //Generate unsaturated signal from integrator only
        integrator_unsat = ki*integrator;

        //Saturate the integrator to the limit
        integrator = saturate(integrator_unsat)/ki;
    }

    //PID control
    if(flag == true){
        //Differentiate error
        error_dot = beta * error_dot + (((1 - beta)/Ts) * (error - error_d1));

        //PID control
        u_unsat = (kp*error) + (ki * integrator) + (kd * error_dot);
    }

    else{
        //differentiate y
        y_dot = beta * y_dot + (((1 - beta) / Ts) * (y - y_d1));

        //PID control
        u_unsat = (kp*error) + (ki * integrator) - (kd * y_dot);
    }

    //Return saturated control signal
    double u_sat = saturate(u_unsat);



    //Integrator anti-windup beard
    // if(ki != 0.0){
    //     integrator = integrator + ((1.0 / ki) * (u_sat - u_unsat));
    // }

    //Update delayed variables
    error_d1 = error;
    y_d1 = y;
    return u_sat;
}

//PD calculation
double PIDControl::PD(double y_r, double y){
//Initialize variables to prevent compiler errors
    double u_unsat;

    //Compute the current error
    double error = y_r - y;

    //Integrate errkor using trapazoidal rule
    integrator = integrator + ((Ts/2) * (error + error_d1));

    //PID control
    if(flag == true){
        //Differentiate error
        error_dot = beta * error_dot + (((1 - beta)/Ts) * (error - error_d1));

        //PID control
        u_unsat = (kp*error) + (kd * error_dot);
    }

    else{
        //differentiate y
        y_dot = beta * y_dot + (((1 - beta) / Ts) * (y - y_d1));

        //PID control
        u_unsat = (kp*error) - (kd * y_dot);
    }

    //Return saturated control signal
    double u_sat = saturate(u_unsat);

    //Update delayed variables
    error_d1 = error;
    y_d1 = y;
    return u_sat;
}

//Saturation check (from beard)
// double PIDControl::saturate(double u){
//     //Check if absolute value is above limit, clip value if so
//     if (abs(u) > limit){
//         u = limit * (abs(u) / u);
//     }
//     return u;
// }

//Saturation considering two bounds not equal to each other
double PIDControl::saturate(double u){
    return max(min(upperLimit, u), lowerLimit);
}

void PIDControl::update_time_parameters(double t, double s){
    Ts = t;
    sigma = s;
    beta = (2.0*sigma - Ts) / (2.0*sigma + Ts);
}

void PIDControl::update_gains(double p, double i, double d){
    kp = p;
    ki = i;
    kd = d;
}

void PIDControl::setpoint_reset(double y_r, double y){
    // Reset the critical controller values to prevent instant setpoint change from
    // ruining the response
    integrator = 0;
    error_d1 = y_r - y;
    error_dot = 0;
}