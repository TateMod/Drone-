#ifndef IMU_HPP
#define IMU_HPP
#include <array>
#include <cstdint>
#include "MPU9250.hpp"



class IMU {
public:
    IMU();          // like constructure but for whle thing
      std::array<float, 3> readGyro();                       // function declared but donest taeka nything in
      void accellAngles(); 
      void gyroAngles();// 3 g values
      void complimentoryFilter();
      float getFinalRoll() const { return finalRoll; }
      float getFinalPitch() const { return finalPitch; }



private:
    bool _firstrun;
    
    MPU9250 sensor;

    float ARdegrees = 0;
    float APdegrees = 0;
    float gyroRollAngle = 0;
    float gyroPitchAngle = 0;
    float gyroYawAngle = 0;
    uint64_t start_time;
    float alpha = 0.98;
    float finalRoll = 0;
    float finalPitch = 0;
    





};
#endif