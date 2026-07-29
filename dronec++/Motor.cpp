#include "Motor.hpp"
#include <cmath>
#include <cstdint>
#include "PWM.hpp"
#include <hardware/gpio.h>
#include <pico/types.h>
#include <algorithm>
#include <hardware/pwm.h>




// any other #includes this file's code actually needs (algorithm, cstdint, etc.)

Motor:: Motor()
    : motorPin1(14), motorPin2(15), motorPin3(13), motorPin4(12)
    
     // initializer list — only for members set directly from parameters
{
    gpio_set_function(motorPin1, GPIO_FUNC_PWM);
    uint slice_num1 = pwm_gpio_to_slice_num(motorPin1);
    pwm_set_wrap(slice_num1, 65535);
    pwm_set_enabled(slice_num1, true);
    pwm_set_gpio_level(motorPin1, 3277);

    gpio_set_function(motorPin2, GPIO_FUNC_PWM);
    uint slice_num2 = pwm_gpio_to_slice_num(motorPin2);
    pwm_set_wrap(slice_num2, 65535);
    pwm_set_enabled(slice_num2, true);
    pwm_set_gpio_level(motorPin2, 3277);

    gpio_set_function(motorPin3, GPIO_FUNC_PWM);
    uint slice_num3 = pwm_gpio_to_slice_num(motorPin3);
    pwm_set_wrap(slice_num3, 65535);
    pwm_set_enabled(slice_num3, true);
    pwm_set_gpio_level(motorPin3, 3277);

    gpio_set_function(motorPin4, GPIO_FUNC_PWM);
    uint slice_num4 = pwm_gpio_to_slice_num(motorPin4);
    pwm_set_wrap(slice_num4, 65535);
    pwm_set_enabled(slice_num4, true);
    pwm_set_gpio_level(motorPin4, 3277);







}

void Motor:: motorProcessing(int throttle, float roll_correction,float  pitch_correction, float yaw_correction){

    motorPitch = pitch_correction;
    motorRoll = roll_correction;
    motorThrottle = throttle;
    motorYaw = yaw_correction;


}

void Motor::motorMixing(){
        motor1_pwm = motorThrottle + motorRoll + motorPitch + motorYaw;  // FL
        motor2_pwm = motorThrottle + motorRoll - motorPitch - motorYaw ; // BL
        motor3_pwm = motorThrottle - motorRoll - motorPitch + motorYaw  ;// BR
        motor4_pwm = motorThrottle - motorRoll + motorPitch - motorYaw  ;// FR
        if (motorThrottle <= 1050){
            //pwm u16 lowest
            pwm_set_gpio_level(motorPin1, 3277);
            pwm_set_gpio_level(motorPin2, 3277);
            pwm_set_gpio_level(motorPin3, 3277);
            pwm_set_gpio_level(motorPin4, 3277);



        }else{
            // map pwm to joystick
            



            pwm_set_gpio_level(motorPin1, std::clamp(pwm.PWMmap(motor1_pwm), 3277,  6554));
            pwm_set_gpio_level(motorPin2, std::clamp(pwm.PWMmap(motor2_pwm), 3277,  6554));
            pwm_set_gpio_level(motorPin3, std::clamp(pwm.PWMmap(motor3_pwm), 3277,  6554));
            pwm_set_gpio_level(motorPin4, std::clamp(pwm.PWMmap(motor4_pwm), 3277,  6554));
           
 

        }

    }


void Motor::motorOFF(){
    pwm_set_gpio_level(motorPin1, 3277);
    pwm_set_gpio_level(motorPin2, 3277);
    pwm_set_gpio_level(motorPin3, 3277);
    pwm_set_gpio_level(motorPin4, 3277);



}

// repeat the ClassName:: pattern for every method declared in the header