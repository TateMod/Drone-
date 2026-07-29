#include <cstdint>
#include <array>
#ifndef MPU9250_HPP
#define MPU9250_HPP


class MPU9250{
    public:
        void setup();
        MPU9250(int sda_pin, int scl_pin);



        std::array<int16_t, 3> readGyroRaw();
        std::array<float, 3> readGyro();
        std::array<int16_t, 3> readAccelRaw();
        std::array<float, 3> readAccel();
        std::array<float, 3> calibrate();

        float ax, ay, az;
        float gx, gy, gz;

        
        float getgx() const { return gx; }
        float getgy() const { return gy; }
        float getgz() const { return gz; }

        


    private:
        int sample = 250;
        uint8_t reg;
        uint8_t buffer;
        static constexpr uint8_t REG_PWR_MGMT_1 = 0x6B;
        static constexpr uint8_t IMU_I2C_ADDRESS = 0x68;
        static constexpr uint8_t REG_WHO_AM_I = 0x75;
        static constexpr uint8_t EXPECTED_ID = 0x74;
        static constexpr uint8_t REG_ACCEL_XOUT_H=0x3B;
        static constexpr uint8_t REG_GYRO_XOUT_H=0x43;
        float ACCEL_SCALE_MODIFIER = 16384.0;
        float GYRO_SCALE_MODIFIER = 131.0;
        static constexpr uint8_t  ACCEL_CONFIG = 0x1c;
        static constexpr uint8_t ACCEL_CONFIG_2 = 0x1d;
        static constexpr uint8_t GYRO_CONFIG = 0x1b;
        static constexpr uint8_t CONFIG = 0x1a;


        float offset_ax = -92.836;    // all 0 for recalibration
        float offset_ay = 25.464;
        float offset_az = -166.94824;
        float offset_gx = -577.092;
        float offset_gy = -43.348;
        float offset_gz = -150.704;

        




};
#endif