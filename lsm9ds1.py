import machine
import struct
import time
from micropython import const

# Registers & Constants
_LSM9DS1_ADDRESS_ACCELGYRO = const(0x6B)
_LSM9DS1_ADDRESS_MAG = const(0x1E)
_LSM9DS1_XG_ID = const(0b01101000)
_LSM9DS1_MAG_ID = const(0b00111101)

# Linear Acceleration: mg per LSB
_LSM9DS1_ACCEL_MG_LSB_2G = 0.061
_LSM9DS1_ACCEL_MG_LSB_4G = 0.122
_LSM9DS1_ACCEL_MG_LSB_8G = 0.244
_LSM9DS1_ACCEL_MG_LSB_16G = 0.732

# Magnetic Field: mgauss per LSB
_LSM9DS1_MAG_MGAUSS_4GAUSS = 0.14
_LSM9DS1_MAG_MGAUSS_8GAUSS = 0.29
_LSM9DS1_MAG_MGAUSS_12GAUSS = 0.43
_LSM9DS1_MAG_MGAUSS_16GAUSS = 0.58

# Gyroscope: dps per LSB
_LSM9DS1_GYRO_DPS_DIGIT_245DPS = 0.00875
_LSM9DS1_GYRO_DPS_DIGIT_500DPS = 0.01750
_LSM9DS1_GYRO_DPS_DIGIT_2000DPS = 0.07000

# Registers
_LSM9DS1_REGISTER_WHO_AM_I_XG = const(0x0F)
_LSM9DS1_REGISTER_CTRL_REG1_G = const(0x10)
_LSM9DS1_REGISTER_CTRL_REG2_G = const(0x11)
_LSM9DS1_REGISTER_CTRL_REG3_G = const(0x12)
_LSM9DS1_REGISTER_CTRL_REG4 = const(0x1E)
_LSM9DS1_REGISTER_CTRL_REG5_XL = const(0x1F)
_LSM9DS1_REGISTER_CTRL_REG6_XL = const(0x20)
_LSM9DS1_REGISTER_CTRL_REG7_XL = const(0x21)
_LSM9DS1_REGISTER_CTRL_REG8 = const(0x22)

_LSM9DS1_REGISTER_OUT_X_L_G = const(0x18)
_LSM9DS1_REGISTER_OUT_X_L_XL = const(0x28)
_LSM9DS1_REGISTER_OUT_X_L_M = const(0x28)

_LSM9DS1_REGISTER_WHO_AM_I_M = const(0x0F)
_LSM9DS1_REGISTER_CTRL_REG1_M = const(0x20)
_LSM9DS1_REGISTER_CTRL_REG2_M = const(0x21)
_LSM9DS1_REGISTER_CTRL_REG3_M = const(0x22)

# User Constants
ACCELRANGE_2G = 0b00 << 3
ACCELRANGE_16G = 0b01 << 3
ACCELRANGE_4G = 0b10 << 3
ACCELRANGE_8G = 0b11 << 3
MAGGAIN_4GAUSS = 0b00 << 5
GYROSCALE_500DPS = 0b00 << 3#was 245

class LSM9DS1:
    def __init__(self, i2c):
        self.i2c = i2c
        # Soft reset & reboot accel/gyro
        self._write_u8(_LSM9DS1_ADDRESS_ACCELGYRO, _LSM9DS1_REGISTER_CTRL_REG8, 0x05)
        # Soft reset & reboot magnetometer
        self._write_u8(_LSM9DS1_ADDRESS_MAG, _LSM9DS1_REGISTER_CTRL_REG2_M, 0x0C)
        time.sleep(0.01)
        # ADD after time.sleep(0.01) in __init__
        self._write_u8(_LSM9DS1_ADDRESS_ACCELGYRO, _LSM9DS1_REGISTER_CTRL_REG8, 0x44)

        # Enable Gyro (Continuous)
        self._write_u8(_LSM9DS1_ADDRESS_ACCELGYRO, _LSM9DS1_REGISTER_CTRL_REG1_G, 0xC0)#was 0xc8
        # Enable Accel (Continuous)
        self._write_u8(_LSM9DS1_ADDRESS_ACCELGYRO, _LSM9DS1_REGISTER_CTRL_REG5_XL, 0x38)
        self._write_u8(_LSM9DS1_ADDRESS_ACCELGYRO, _LSM9DS1_REGISTER_CTRL_REG6_XL, 0xC0)
        # Enable Mag (Continuous)
        self._write_u8(_LSM9DS1_ADDRESS_MAG, _LSM9DS1_REGISTER_CTRL_REG3_M, 0x00)

    def _write_u8(self, address, reg, value):
        self.i2c.writeto_mem(address, reg, bytes([value]))

    def _read_bytes(self, address, reg, count):
        # We add 0x80 to the register address to enable AUTO-INCREMENT
        # This solves the "frozen data" issue you were having!
        return self.i2c.readfrom_mem(address, reg | 0x80, count)

    def read_accel(self):
        # Read 6 bytes starting from OUT_X_L_XL
        data = self._read_bytes(_LSM9DS1_ADDRESS_ACCELGYRO, _LSM9DS1_REGISTER_OUT_X_L_XL, 6)
        raw_x, raw_y, raw_z = struct.unpack_from("<hhh", data)
        # Convert to Gs (assuming default 2G range)
        scale = _LSM9DS1_ACCEL_MG_LSB_2G / 1000.0
        return raw_x * scale, raw_y * scale, raw_z * scale

    def read_gyro(self):
        data = self._read_bytes(_LSM9DS1_ADDRESS_ACCELGYRO, _LSM9DS1_REGISTER_OUT_X_L_G, 6)
        raw_x, raw_y, raw_z = struct.unpack_from("<hhh", data)
        # Convert to DPS (assuming default 500dps)
        scale = _LSM9DS1_GYRO_DPS_DIGIT_245DPS#was500
        return raw_x * scale, raw_y * scale, raw_z * scale

    def read_mag(self):
        data = self._read_bytes(_LSM9DS1_ADDRESS_MAG, _LSM9DS1_REGISTER_OUT_X_L_M, 6)
        raw_x, raw_y, raw_z = struct.unpack_from("<hhh", data)
        # Convert to Gauss (assuming default 4G)
        scale = _LSM9DS1_MAG_MGAUSS_4GAUSS / 1000.0
        return raw_x * scale, raw_y * scale, raw_z * scale
