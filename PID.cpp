#include <cstdint>
#include "PID.hpp"
#include <algorithm>
#include <hardware/timer.h>

PID::PID(float kp, float ki, float kd)// constructor takes in pid values
    : kp(kp), ki(ki), kd(kd), d_filter(20.0f, 100.0f)// defines teh constructor values
{
    start_time = time_us_64();// starting time for PID temp varabul in constructer doens need to be initalised
}

float PID::computePID(float target, float current_value, const float* gyro_rate) {
    // all the actual PID math goes here — this is the real "body" of your Python computePID

    uint64_t now = time_us_64();
    float dt = (now - start_time) / 1e6f;   // microseconds → seconds
    start_time = now;

// get error
    float error = target - current_value;
    // p term 
    float p_term = kp * error;
    // i term with clamp
    accumulated_error += error * dt;
    accumulated_error = std::clamp(accumulated_error, -50.0f, 50.0f);
    
    float d_term;

    float i_term = ki * accumulated_error;
    // d term
    if (gyro_rate != nullptr) {
        d_term = -kd * d_filter.update(*gyro_rate); //* is derefrecnig so sayinguses the info inside not jus teh placholder


    }else{
       
        
        float error_change;
        if (dt > 0) {
            error_change = (error - last_error) / dt;
        } else {
        error_change = 0.0f;
        }
        d_term = kd * error_change;
    }
    last_error = error;
    return p_term + i_term + d_term;






}

void PID:: reset(){//dont add anything back jsut resets state
    accumulated_error = 0;
    last_error = 0;
    d_filter.reset();
    start_time = time_us_64();

}







