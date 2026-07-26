#include "MPU9250.hpp"
#include <hardware/i2c.h>
#include <cstdint>
#include <algorithm>
#include <array>

MPU9250::MPU9250(int SDA, int SCL) {
    // Constructor
}

void MPU9250::setup() {
    uint8_t buffer[2];

    // Turn on chip
    buffer[0] = REG_PWR_MGMT_1;
    buffer[1] = 0x01;
    i2c_write_blocking(i2c0, IMU_I2C_ADDRESS, buffer, 2, false);

    // Gyro
    buffer[0] = GYRO_CONFIG;
    buffer[1] = 0x00;
    i2c_write_blocking(i2c0, IMU_I2C_ADDRESS, buffer, 2, false);

    buffer[0] = CONFIG;
    buffer[1] = 0x03;
    i2c_write_blocking(i2c0, IMU_I2C_ADDRESS, buffer, 2, false);

    // Accel
    buffer[0] = ACCEL_CONFIG;
    buffer[1] = 0x00;
    i2c_write_blocking(i2c0, IMU_I2C_ADDRESS, buffer, 2, false);

    buffer[0] = ACCEL_CONFIG_2;
    buffer[1] = 0x03;
    i2c_write_blocking(i2c0, IMU_I2C_ADDRESS, buffer, 2, false);
}

std::array<int16_t, 3> MPU9250::readGyroRaw() {
    uint8_t reg = REG_GYRO_XOUT_H;
    i2c_write_blocking(i2c0, IMU_I2C_ADDRESS, &reg, 1, true);
    uint8_t rawGyroData[6];
    i2c_read_blocking(i2c0, IMU_I2C_ADDRESS, rawGyroData, 6, false);

    int16_t gyro_x = (rawGyroData[0] << 8) | rawGyroData[1];
    int16_t gyro_y = (rawGyroData[2] << 8) | rawGyroData[3];
    int16_t gyro_z = (rawGyroData[4] << 8) | rawGyroData[5];

    return {gyro_x, gyro_y, gyro_z};
}

std::array<int16_t, 3> MPU9250::readAccelRaw() {
    uint8_t reg = REG_ACCEL_XOUT_H;
    i2c_write_blocking(i2c0, IMU_I2C_ADDRESS, &reg, 1, true);
    uint8_t rawAccelData[6];
    i2c_read_blocking(i2c0, IMU_I2C_ADDRESS, rawAccelData, 6, false);

    int16_t accel_x = (rawAccelData[0] << 8) | rawAccelData[1];
    int16_t accel_y = (rawAccelData[2] << 8) | rawAccelData[3];
    int16_t accel_z = (rawAccelData[4] << 8) | rawAccelData[5];

    return {accel_x, accel_y, accel_z};
}

std::array<float, 3> MPU9250::readGyro() {
    std::array<int16_t, 3> rawGyro = readGyroRaw();
    float gx = (rawGyro[0] - offset_gx) / GYRO_SCALE_MODIFIER;
    float gy = (rawGyro[1] - offset_gy) / GYRO_SCALE_MODIFIER;
    float gz = (rawGyro[2] - offset_gz) / GYRO_SCALE_MODIFIER;
    return {gx, gy, gz};
}

std::array<float, 3> MPU9250::readAccel() {
    std::array<int16_t, 3> rawAccel = readAccelRaw();
    float ax = (rawAccel[0] - offset_ax) / ACCEL_SCALE_MODIFIER;
    float ay = (rawAccel[1] - offset_ay) / ACCEL_SCALE_MODIFIER;
    float az = (rawAccel[2] - offset_az) / ACCEL_SCALE_MODIFIER;
    return {ax, ay, az};
}

std::array<float, 3> MPU9250::calibrate() {
    float sumAX = 0, sumAY = 0, sumAZ = 0;
    float sumGX = 0, sumGY = 0, sumGZ = 0;

    for (int i = 0; i < sample; i++) {
        std::array<int16_t, 3> rawAccel = readAccelRaw();
        sumAX += rawAccel[0];
        sumAY += rawAccel[1];
        sumAZ += rawAccel[2];

        std::array<int16_t, 3> rawGyro = readGyroRaw();
        sumGX += rawGyro[0];
        sumGY += rawGyro[1];
        sumGZ += rawGyro[2];
    }

    offset_ax = sumAX / sample;
    offset_ay = sumAY / sample;
    offset_az = (sumAZ / sample) - ACCEL_SCALE_MODIFIER;

    offset_gx = sumGX / sample;
    offset_gy = sumGY / sample;
    offset_gz = sumGZ / sample;

    return {offset_ax, offset_ay, offset_az};
}