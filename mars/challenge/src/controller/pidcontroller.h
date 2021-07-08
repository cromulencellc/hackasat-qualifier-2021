#ifndef __PID_H__
#define __PID_H__

#include <stdint.h>

class PID
{
public:
	PID(float Kp, float Ki, float Kd, float initialVelocity, 
    float finalVelocity, float initialAltitude, float finalAltitude);

    float pid_output;
    void update(float new_value);

private:

    double get_setpoint();

    double epoch_seconds;
    double last_seconds;
    float p_initial_altitude;
    float p_final_altitude;
    float p_initial_velocity;
    float p_final_velocity;
    float p_delta_altitude;
    float p_planned_acceleration;
    float p_integral_error;  // cumulative error
    float p_last_error;      
    uint32_t p_epoch_time_s;    // when the controller was instantiated
    uint32_t p_epoch_time_us;
    uint32_t p_last_time;
    uint32_t p_delta_ms_since_epoch;
    double Kp;  // proportional error coefficient
    double Ki;  // integral error coefficient
    double Kd;  // derivative error coefficient

};

#endif // __PID_H__


