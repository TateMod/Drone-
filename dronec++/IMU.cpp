#include "IMU.hpp"
#include <cmath>
#include <cstdint>
#include "hardware/clocks.h"
#include <hardware/timer.h>
#include "MPU9250.hpp"

// any other #includes this file's code actually needs (algorithm, cstdint, etc.)

IMU::IMU() : sensor(4, 5)
     // initializer list — only for members set directly from parameters
{
    start_time = time_us_64();// constructor body — anything needing a function call (like time_us_64()) goes here instead
}


std::array<float, 3> IMU::readGyro() {
    return sensor.readGyro();
}




void IMU::accellAngles() {
    std::array<float, 3> a = sensor.readAccel();

    float Aroll = std::atan2(a[1], a[2]);
    ARdegrees = Aroll * (180/ M_PI);
    float Apitch = std::atan2(-a[0], std::sqrt(a[1]* a[1] + a[2] * a[2]));
    APdegrees = Apitch * (180 /  M_PI);

    // the real logic goes here — every calculation, every if/else, everything
    // that was just a signature in the header now has its full body
}

void IMU :: gyroAngles(){

    
    uint64_t now = time_us_64();
    float dt = (now - start_time) / 1e6f;   // microseconds → seconds
    start_time = now;
    std::array<float, 3> g = sensor.readGyro();
    gyroRollAngle += g[0] * dt;
    gyroPitchAngle += g[1] * dt;
    gyroYawAngle += g[2] * dt;



}

void IMU::complimentoryFilter(){
    if (_firstrun == true){

        gyroRollAngle = ARdegrees;
        gyroPitchAngle = APdegrees;
        _firstrun = false;
    }else{

        finalRoll = (alpha * gyroRollAngle) + ((1 - alpha) * ARdegrees) ;
        finalPitch = (alpha * gyroPitchAngle) + ((1 - alpha) * APdegrees) ;
        gyroRollAngle = finalRoll;
        gyroPitchAngle = finalPitch;
    }

}




// repeat the ClassName:: pattern for every method declared in the header