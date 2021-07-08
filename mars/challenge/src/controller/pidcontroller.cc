
#include "pidcontroller.h"
#include <stdint.h>
#include "common.h"


void ReadClock( uint32_t *seconds, uint32_t *microseconds );

PID::PID(float Kp, float Ki, float Kd, float initialVelocity, 
    float finalVelocity, float initialAltitude, float finalAltitude)   
{

    ReadClock(&p_epoch_time_s, &p_epoch_time_us);

    epoch_seconds = (double)p_epoch_time_s + (double)p_epoch_time_us/1000000.0;
    last_seconds = epoch_seconds;

    p_delta_ms_since_epoch = 0;
    PID::Kp =Kp;
    PID::Ki =Ki;
    PID::Kd =Kd;
    p_initial_velocity=initialVelocity;
    p_final_velocity=finalVelocity;
    p_initial_altitude=initialAltitude;
    p_final_altitude=finalAltitude;
    p_last_error = 0;

    p_delta_altitude = finalAltitude - initialAltitude;

    p_planned_acceleration = (finalVelocity * finalVelocity - initialVelocity * initialVelocity)/ 2 / p_delta_altitude;
    

    // debug_log(LOG_PRIORITY_HIGH, "epoch = %u\n", p_epoch_time);
    // debug_log(LOG_PRIORITY_HIGH, "delta altitude = %u\n", (uint32_t)p_delta_altitude);
}

// based upon the ramp specified when the controller was created, calculate where on the line it should be at this point
double PID::get_setpoint()
{

    double delta_seconds = p_delta_ms_since_epoch/1000.0;

    // debug_log(LOG_PRIORITY_HIGH, "delta = %u\n", (unsigned int)delta_seconds);

    double planned_position = p_initial_altitude + p_initial_velocity * delta_seconds + .5 * p_planned_acceleration * delta_seconds * delta_seconds;

    return planned_position;

}

void PID::update(float current_position)
{

uint32_t current_time_s;
uint32_t current_time_us;
double current_time_float;
uint32_t delta_ms;

    ReadClock(&current_time_s, &current_time_us);

    current_time_float = (double)current_time_s + (double)current_time_us/1000000.0;

    delta_ms = (current_time_float - last_seconds) * 1000;

    uint32_t delta_time_s = current_time_s - p_epoch_time_s;
    int32_t delta_time_us = current_time_us - p_epoch_time_us;

    p_delta_ms_since_epoch = delta_time_s * 1000 + delta_time_us / 1000;

    last_seconds = current_time_float;
    
    double planned_position = get_setpoint();
    
    if (planned_position < 0.0) {

        planned_position = 0.0;
    }
    // debug_log(LOG_PRIORITY_HIGH, "position = %d\n", (int)error);
    double position_error = planned_position - current_position;

    double delta_seconds = delta_ms / 1000.0;

    p_integral_error += position_error * delta_seconds;

    // debug_log(LOG_PRIORITY_HIGH, "i_error = %d\n", (int)p_integral_error);

    double derivative_error = (abs(position_error) - abs(p_last_error))/delta_seconds;

    // debug_log(LOG_PRIORITY_HIGH, "d_error = %d\n", (int)derivative_error);

    p_last_error = position_error;

    pid_output = Kp * position_error + Ki * p_integral_error + Kd * derivative_error;

    debug_log(LOG_PRIORITY_HIGH, "time: %u, p_error = %d, i_error = %d, d_error = %d, PID_OUTPUT = %d", 
            (unsigned int) p_delta_ms_since_epoch, (int)position_error, (int)p_integral_error, (int)derivative_error, (int)(pid_output));

}
