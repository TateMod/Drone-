
#include "hight.hpp"
#include <cstdint>



hight::hight() {
    prev_throttle = 0;
    target_hight_set = false;//is it typenull
    


}

float hight::hight_check(float throttle){

    
    uint16_t distance;
    droneTOF.VL53L1X_GetDistance(&distance);


    float tof_h = distance /10;
    float hight_correction;

    if( throttle == prev_throttle){
        if (target_hight_set == false){
            target_hight = tof_h;
            target_hight_set = true;
        }
         hight_correction = hightPID.computePID( target_hight, tof_h, nullptr);


    }else{
        target_hight_set = false;
        hight_correction = 0.0;

        
    }
    prev_throttle = throttle;
    return hight_correction;


}