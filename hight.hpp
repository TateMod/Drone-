
#ifndef hight_HPP
#define hight_HPP
#include <cstdint>
//#include "vl53l1x_class.h"
#include "PID.hpp"
#include "VL53L1X.hpp"

class hight{
    public:
        hight();
        //wat can anyone access
        float hight_check( float throttle);
        VL53L1X droneTOF;// need to add


    
    private:

        //DroneTOF droneTOF;
        PID hightPID;
        float target_hight;
        float prev_throttle; //could be int
        bool target_hight_set;
        


};
#endif