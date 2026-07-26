
#include"PWM.hpp"

PWM :: PWM(){

//constructor
}

   int PWM::PWMmap(float motor){

        return static_cast<int> ((motor - inMin) * (outMax - outMin) / (inMax - inMin) + outMin);


   
}