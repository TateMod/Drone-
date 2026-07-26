#ifndef Motor_HPP
#define Motor_HPP
#include <array>
#include <cstdint>
#include "PWM.hpp"



class Motor {
public:
    Motor();          // like constructure but for whle thing
                               // function declared but donest taeka nything in
    void motorProcessing( int throttle, float roll_correction, float pitch_correction,float yaw_correction);

    void motorMixing();

    void motorOFF();

private:
    
    
    PWM pwm;
    int motorPin1;
    int motorPin2;
    int motorPin3;
    int motorPin4;

    float motorPitch;
    float motorRoll;
    float motorThrottle;
    float motorYaw;
    float motor1_pwm;
    float motor2_pwm;
    float motor3_pwm;
    float motor4_pwm;





};
#endif