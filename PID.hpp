#include"Biquad.hpp"

#ifndef PID_HPP
#define PID_HPP



class PID {
public:
    PID(float kp, float ki, float kd);          // like constructure but for whle thing
    float computePID(float target, float current_value, const float* gyro_rate);  // takes in for te fucntion
    void reset();                                 // function declared but donest taeka nything in

private:
    float kp;
    float ki;
    float kd;
    float accumulated_error;
    float last_error;
    uint64_t start_time;
    Biquadfilter d_filter;
};
#endif