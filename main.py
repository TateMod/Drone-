import machine
from machine import UART, Pin
import time
import lsm9ds1
import math
import struct
import VL53L1X
import network
import socket

# PMW3901 optical flow sensor register addresses
REG_ID = 0x00
REG_DATA_READY = 0x02
REG_MOTION_BURST = 0x16          # burst read register for motion data
REG_POWER_UP_RESET = 0x3a        # reset register written on startup
REG_ORIENTATION = 0x5b
WAIT = -1                         # sentinel value used in bulk write sequences to trigger a delay
REG_RAWDATA_GRAB = 0x58
REG_RAWDATA_GRAB_STATUS = 0x59

# WiFi access point broadcasting its own network for telemetry
ap = network.WLAN(network.AP_IF)
ap.config(essid='Pico-Drone', password='password123')
ap.active(True)
print("AP active:", ap.ifconfig()[0])

# UDP broadcast socket with telemetry sent to all devices on the network
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
target_ip = '192.168.4.255'
target_port = 5005

# Physical button on GPIO20 used to trigger gyroscope calibration on startup
calibrate_button = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_UP)


class positionHold():
    def __init__(self, flow_sensor, pid_roll, pid_pitch):
        self.sensor = flow_sensor
        self.flowRollPID = pid_roll
        self.flowPitchPID = pid_pitch
        self.GYRO_TO_FLOW_SCALER = 1.2   # tuned scaling factor to match gyro units to optical flow pixel units
        self.MAX_ANGLE = 15.0             # maximum correction angle in degrees to prevent excessive tilt from position hold
        self.last_dx = 0
        self.last_dy = 0

    def process(self, gyro_x, gyro_y):
        raw_dx, raw_dy = self.sensor.get_motion()
        # subtract gyroscope rotation contribution from raw flow reading
        # prevents tilting to correct sensor from reporting false horizontal movement
        compensated_dx = raw_dx - (gyro_x * self.GYRO_TO_FLOW_SCALER)
        compensated_dy = raw_dy - (gyro_y * self.GYRO_TO_FLOW_SCALER)
        # outer PID loop targets zero movement any detected movement produces a corrective angle
        target_roll = self.flowRollPID.computePID(0.0, compensated_dx)
        target_pitch = self.flowPitchPID.computePID(0.0, compensated_dy)
        # clamp correction to prevent position hold commanding excessive tilt
        target_roll = max(-self.MAX_ANGLE, min(self.MAX_ANGLE, target_roll))
        target_pitch = max(-self.MAX_ANGLE, min(self.MAX_ANGLE, target_pitch))
        self.last_dx = compensated_dx
        self.last_dy = compensated_dy
        # returned as target angles fed into the inner attitude PID loop
        return target_roll, target_pitch


class opticalFlow():
    def __init__(self):
        # SPI0 at 400kHz - PMW3901 maximum supported rate
        self.spi = machine.SPI(0, baudrate=400000, polarity=0, phase=0,
                               sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
        self.cs = machine.Pin(17, machine.Pin.OUT)
        time.sleep(0.05)                          # allow sensor to power up before communication
        self._write(REG_POWER_UP_RESET, 0x5a)     # trigger hardware reset
        time.sleep(0.02)
        for offset in range(5):                   # clear motion registers after reset
            self._read(REG_DATA_READY + offset)
        self._secret_sauce()                      # manufacturer specified initialisation sequence

    def _bulk_write(self, data):
        # writes pairs of [register, value] from a flat list
        # WAIT sentinel triggers a delay in milliseconds instead of a write
        for x in range(0, len(data), 2):
            register, value = data[x:x + 2]
            if register == WAIT:
                time.sleep(value / 1000)
            else:
                self._write(register, value)

    def _secret_sauce(self):
        # manufacturer specified register initialisation sequence from PMW3901 datasheet
        # required for correct sensor operation - DO NOT MODIFY VALUES
        self._bulk_write([
            0x7f, 0x00, 0x55, 0x01, 0x50, 0x07,
            0x7f, 0x0e, 0x43, 0x10
        ])
        # select performance register value based on sensor variant
        if self._read(0x67) & 0b10000000:
            self._write(0x48, 0x04)
        else:
            self._write(0x48, 0x02)
        self._bulk_write([
            0x7f, 0x00, 0x51, 0x7b,
            0x50, 0x00, 0x55, 0x00, 0x7f, 0x0E
        ])
        if self._read(0x73) == 0x00:
            # read calibration values from sensor and apply mathematical adjustment
            c1 = self._read(0x70)
            c2 = self._read(0x71)
            if c1 <= 28:
                c1 += 14
            if c1 > 28:
                c1 += 11
            c1 = max(0, min(0x3F, c1))   # clamp to valid register range
            c2 = (c2 * 45) // 100
            self._bulk_write([
                0x7f, 0x00, 0x61, 0xad,
                0x51, 0x70, 0x7f, 0x0e
            ])
            self._write(0x70, c1)
            self._write(0x71, c2)
        self._bulk_write([
            0x7f, 0x00, 0x61, 0xad, 0x7f, 0x03, 0x40, 0x00, 0x7f, 0x05,
            0x41, 0xb3, 0x43, 0xf1, 0x45, 0x14, 0x5b, 0x32, 0x5f, 0x34,
            0x7b, 0x08, 0x7f, 0x06, 0x44, 0x1b, 0x40, 0xbf, 0x4e, 0x3f,
            0x7f, 0x08, 0x65, 0x20, 0x6a, 0x18, 0x7f, 0x09, 0x4f, 0xaf,
            0x5f, 0x40, 0x48, 0x80, 0x49, 0x80, 0x57, 0x77, 0x60, 0x78,
            0x61, 0x78, 0x62, 0x08, 0x63, 0x50, 0x7f, 0x0a, 0x45, 0x60,
            0x7f, 0x00, 0x4d, 0x11, 0x55, 0x80, 0x74, 0x21, 0x75, 0x1f,
            0x4a, 0x78, 0x4b, 0x78, 0x44, 0x08, 0x45, 0x50, 0x64, 0xff,
            0x65, 0x1f, 0x7f, 0x14, 0x65, 0x67, 0x66, 0x08, 0x63, 0x70,
            0x7f, 0x15, 0x48, 0x48, 0x7f, 0x07, 0x41, 0x0d, 0x43, 0x14,
            0x4b, 0x0e, 0x45, 0x0f, 0x44, 0x42, 0x4c, 0x80, 0x7f, 0x10,
            0x5b, 0x02, 0x7f, 0x07, 0x40, 0x41, 0x70, 0x00,
            WAIT, 0x0A,
            0x32, 0x44, 0x7f, 0x07, 0x40, 0x40, 0x7f, 0x06, 0x62, 0xf0,
            0x63, 0x00, 0x7f, 0x0d, 0x48, 0xc0, 0x6f, 0xd5, 0x7f, 0x00,
            0x5b, 0xa0, 0x4e, 0xa8, 0x5a, 0x50, 0x40, 0x80,
            WAIT, 0xF0,
            0x7f, 0x14, 0x6f, 0x1c, 0x7f, 0x00
        ])

    def _write(self, register, value):
        self.cs.value(0)
        self.spi.write(bytes([register | 0x80, value]))  # MSB set indicates write operation
        self.cs.value(1)

    def _read(self, register, length=1):
        result = []
        buffer = bytearray(2)
        for x in range(length):
            self.cs.value(0)
            self.spi.write_readinto(bytes([register + x, 0]), buffer)  # send register address and read response
            self.cs.value(1)
            result.append(buffer[1])
        if length == 1:
            return result[0]
        else:
            return result

    def get_motion(self, timeout=0.002):
        in_buffer = bytearray(13)
        out_buffer = bytearray(13)
        out_buffer[0] = REG_MOTION_BURST
        t_start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t_start) < timeout * 1000:
            self.cs.value(0)
            self.spi.write_readinto(out_buffer, in_buffer)  # burst read all motion data in single SPI transaction
            self.cs.value(1)
            (_, dr, obs, x, y, quality, raw_sum, raw_max, raw_min,
             shutter_upper, shutter_lower) = struct.unpack("<BBBhhBBBBBB", in_buffer)
            # validate data ready flag and reject low quality readings (quality < 25 with maxed shutter)
            if dr & 0b10000000 and not (quality < 0x19 and shutter_upper == 0x1f):
                return x, y
        return 0, 0  # return zero movement if no valid data within timeout


class tof():
    def __init__(self):
        # I2C0 shared with IMU at 400kHz fast mode
        self.i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4), freq=400000)
        self.sensor = VL53L1X.VL53L1X(self.i2c, 0x29)  # default I2C address 0x29
        self.hight = 0

    def readDistance(self):
        raw = self.sensor.read()
        self.hight = 0.9 * self.hight + 0.1 * raw  # first order low pass filter alpha=0.1 smooths sensor noise


class imu():
    def __init__(self):
        # I2C0 shared with TOF sensor
        self.i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4), freq=400000)
        self.sensor = lsm9ds1.LSM9DS1(self.i2c)
        # hard iron offset corrections determined during magnetometer calibration
        self.mag_offset_x = 0.16002001
        self.mag_offset_y = 0.04101999
        self.mag_offset_z = -0.36232
        
        self.Mheading = 0
        self.accel_logic = 0.732
        self.gyro_logic = 70
        self.mag_logic = 0.29
        
        self.start_time = time.ticks_ms()
        self.gyroRollAngle = 0
        self.gyroPitchAngle = 0
        self.gyroYawAngle = 0
        self.gyroXbias = 0.0   # gyroscope bias offsets calculated during calibration routine
        self.gyroYbias = 0.0
        self.gyroZbias = 0.0
        
        self.alpha = 0.98      # complementary filter trust coefficient - 98% gyroscope, 2% accelerometer
        
        self.finalRoll = 0
        self.finalPitch = 0
        self.finalYaw = 0
        self.calibRoll  = 0.0  # initial roll angle captured during calibration to account for IMU mounting offset
        self.calibPitch = 0.0

        print(self.i2c.scan())
        print("Press button to calibrate...")
        while calibrate_button.value() == 1:  # wait for button press before calibrating
            pass
        print("Button pressed! Place drone still...")
        time.sleep(3)
        self.calibrateGyro()

    def calibrateGyro(self, samples=200):
        # samples gyroscope and accelerometer at rest to calculate bias offsets
        # drone must remain still during 
        print("Keep drone still... calibrating gyro")
        time.sleep(2)
        bx, by, bz = 0, 0, 0
        roll_sum, pitch_sum = 0, 0
        for _ in range(samples):
            g = self.sensor.read_gyro()
            a = self.sensor.read_accel()
            bx += -g[1]
            by += g[0]
            bz += g[2]
            # remap accelerometer axes to match physical sensor orientation on frame
            Xa = a[1]
            Ya = -a[0]
            Za = a[2]
            roll_sum  += math.atan2(Ya, Za) * (180 / math.pi)
            pitch_sum += math.atan2(-Xa, math.sqrt(Ya**2 + Za**2)) * (180 / math.pi)
            time.sleep(0.01)
        self.gyroXbias = bx / samples  # average bias across all samples
        self.gyroYbias = by / samples
        self.gyroZbias = bz / samples
        self.gyroRollAngle  = roll_sum  / samples
        self.gyroPitchAngle = pitch_sum / samples
        self.calibRoll  = self.gyroRollAngle   # store initial angle to compensate for IMU mounting offset
        self.calibPitch = self.gyroPitchAngle
        print(f"Bias X:{self.gyroXbias:.3f} Y:{self.gyroYbias:.3f} Z:{self.gyroZbias:.3f}")
        print(f"Starting angle Roll:{self.gyroRollAngle:.1f} Pitch:{self.gyroPitchAngle:.1f}")
        self.start_time = time.ticks_ms()

    def readIMU(self):
        self.accel = self.sensor.read_accel()
        self.gyro = self.sensor.read_gyro()
        #self.mag = self.sensor.read_mag()

    def readMag(self):
        # subtract hard iron offsets from raw magnetometer readings
        self.Xm = self.mag[0] - self.mag_offset_x
        self.Ym = self.mag[1] - self.mag_offset_y
        self.Zm = self.mag[2] - self.mag_offset_z

    def magCal(self):
        self.XMcal = self.Xm
        self.YMcal = self.Ym
        self.ZMcal = self.Zm

    def magposition(self):
        # tilt compensate magnetometer using filtered roll and pitch angles
        # projects magnetometer axes onto horizontal plane for accurate heading
        roll_rad = math.radians(self.finalRoll)
        pitch_rad = math.radians(self.finalPitch)
        Xh = self.XMcal * math.cos(pitch_rad) + self.ZMcal * math.sin(pitch_rad)
        Yh = self.XMcal * math.sin(roll_rad) * math.sin(pitch_rad) + self.YMcal * math.cos(roll_rad) - self.ZMcal * math.sin(roll_rad) * math.cos(pitch_rad)
        Mposition = math.atan2(Yh, Xh)
        self.Mheading = Mposition * (180 / math.pi)
        if self.Mheading < 0:
            self.Mheading += 360  # convert to 0-360 range

    def readAccell(self):
        # remap accelerometer axes to match physical sensor orientation on frame
        self.Xa = self.accel[1]
        self.Ya = -self.accel[0]
        self.Za = self.accel[2]

    def accellCal(self):
        self.XAcal = self.Xa
        self.YAcal = self.Ya
        self.ZAcal = self.Za

    def accellAngles(self):
        # calculate roll and pitch from gravity vector using atan2
        Aroll = math.atan2(self.YAcal, self.ZAcal)
        self.ARdegrees = Aroll * (180 / math.pi)   # convert radians to degrees
        Apitch = math.atan2(-self.XAcal, math.sqrt(self.YAcal**2 + self.ZAcal**2))
        self.APdegrees = Apitch * (180 / math.pi)

    def readGyro(self):
        # remap gyroscope axes to match physical sensor orientation on frame
        self.Xg = -self.gyro[1]
        self.Yg = self.gyro[0]
        self.Zg = self.gyro[2]

    def gyroCal(self):
        # subtract calibration bias from raw gyroscope readings
        self.XGcal = (self.Xg - self.gyroXbias)
        self.YGcal = (self.Yg - self.gyroYbias)
        self.ZGcal = (self.Zg - self.gyroZbias)

    def gyroAngle(self):
        # numerical integration of gyroscope rate to accumulate angle
        dt = time.ticks_diff(time.ticks_ms(), self.start_time) / 1000
        self.start_time = time.ticks_ms()
        self.gyroRollAngle  += self.XGcal * dt
        self.gyroPitchAngle += self.YGcal * dt
        self.gyroYawAngle   += self.ZGcal * dt

    def complimentoryFilter(self):
        # complementary filter fuses gyroscope and accelerometer estimates
        # alpha=0.98 trusts gyroscope for short term accuracy
        # (1-alpha)=0.02 corrects with accelerometer to prevent long term drift
        self.finalRoll  = (self.alpha * self.gyroRollAngle)  + ((1 - self.alpha) * self.ARdegrees)
        self.finalPitch = (self.alpha * self.gyroPitchAngle) + ((1 - self.alpha) * self.APdegrees)
        self.gyroRollAngle  = self.finalRoll   # reset gyro angle to filter output each loop to prevent drift accumulation
        self.gyroPitchAngle = self.finalPitch

    def updateYaw(self):
        # fuse gyroscope yaw rate with magnetometer heading using complementary filter
        self.finalYaw = self.alpha * self.gyroYawAngle + (1 - self.alpha) * self.Mheading


class BiquadFilter:
    def __init__(self, cutoff_hz, sample_hz):
        # second order Butterworth low pass filter coefficients
        # used on gyroscope D term input to attenuate high frequency noise above cutoff
        w = 2 * math.pi * cutoff_hz / sample_hz
        q = 0.707          # Butterworth maximally flat response
        k = math.tan(w / 2)
        norm = 1 / (1 + k / q + k * k)
        self.b0 = k * k * norm
        self.b1 = 2 * self.b0
        self.b2 = self.b0
        self.a1 = 2 * (k * k - 1) * norm
        self.a2 = (1 - k / q + k * k) * norm
        self.x1 = self.x2 = 0.0  # input history
        self.y1 = self.y2 = 0.0  # output history

    def update(self, x):
        # direct form II transposed biquad implementation
        y = self.b0*x + self.b1*self.x1 + self.b2*self.x2 - self.a1*self.y1 - self.a2*self.y2
        self.x2, self.x1 = self.x1, x
        self.y2, self.y1 = self.y1, y
        return y

    def reset(self):
        self.x1 = self.x2 = 0.0
        self.y1 = self.y2 = 0.0


class PID():
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.accumulated_error = 0
        self.last_error = 0
        self.start_time = time.ticks_ms()
        self.d_filter = BiquadFilter(cutoff_hz=20, sample_hz=100)  # biquad filter on D term - 20Hz cutoff at 100Hz sample rate

    def computePID(self, target, current_value, gyro_rate=None):
        dt = time.ticks_diff(time.ticks_ms(), self.start_time) / 1000
        self.start_time = time.ticks_ms()
        if dt <= 0 or dt > 0.5:  # reject invalid dt to prevents large corrections after timing gaps or first call
            return 0.0

        error = target - current_value
        p_term = self.kp * error  # proportional: responds to current error magnitude

        self.accumulated_error += error * dt
        self.accumulated_error = max(-50, min(50, self.accumulated_error))  # clamp to +-50 to prevent integral windup oscillation
        i_term = self.ki * self.accumulated_error  # integral: eliminates steady state offset over time

        if gyro_rate is not None:
            d_term = -self.kd * self.d_filter.update(gyro_rate)  # derivative from filtered gyro rate - more accurate than error difference
        else:
            error_change = (error - self.last_error) / dt if dt > 0 else 0.0
            d_term = self.kd * error_change  # fallback derivative from error change if no gyro rate supplied

        self.last_error = error
        return p_term + i_term + d_term

    def reset(self):
        # reset all state on disarm to prevent accumulated error affecting next flight
        self.accumulated_error = 0
        self.last_error = 0
        self.d_filter.reset()
        self.start_time = time.ticks_ms()


class remote():
    def __init__(self):
        # UART0 at 115200 baud - iBus protocol from FS-iA6B receiver
        self.uart = UART(0, baudrate=115200, rx=Pin(1))
        self.channels = []
        # initialise channels to safe defaults - centred sticks, minimum throttle
        self.roll = 1500
        self.pitch = 1500
        self.throttle = 1000
        self.yaw = 1500
        self.arming = 0

    def DataParse(self):
        self.data = self.uart.read(32)  # iBus frame is 32 bytes
        if self.data is None:
            return
        if self.data[0] == 0x20 and self.data[1] == 0x40:  # validate iBus header bytes
            self.channels = []
            for i in range(2, len(self.data) - 2, 2):  # skip first 2 header and last 2 checksum bytes
                self.value = (self.data[i + 1] * 256) + self.data[i]  # reconstruct 16-bit value from two bytes little-endian
                self.channels.append(self.value)
            if len(self.channels) >= 4:
                self.roll = self.channels[0]
                self.pitch = self.channels[1]
                self.yaw = self.channels[3]
                if 1000 <= self.channels[2] <= 2000:
                    self.throttle = self.channels[2]
                # clamp channels to valid range - reject corrupt packet values
                if not (1000 <= self.roll  <= 2000): self.roll  = 1500
                if not (1000 <= self.pitch <= 2000): self.pitch = 1500
                if not (1000 <= self.yaw   <= 2000): self.yaw   = 1500
            if len(self.channels) >= 5:
                self.arming = self.channels[4]  # channel 5 used as arming switch


class motor():
    def __init__(self):
        # PWM at 400Hz - BLHeli_S ESC supports higher rates than standard 50Hz for faster correction response
        self.moterPin1 = machine.Pin(11)  # FL - front left
        self.PWMmoterPin1 = machine.PWM(self.moterPin1)
        self.PWMmoterPin1.freq(400)
        self.PWMmoterPin1.duty_u16(3277)  # initialise to minimum throttle (1ms pulse width)

        self.moterPin2 = machine.Pin(14)  # BL - back left
        self.PWMmoterPin2 = machine.PWM(self.moterPin2)
        self.PWMmoterPin2.freq(400)
        self.PWMmoterPin2.duty_u16(3277)

        self.moterPin3 = machine.Pin(12)  # BR - back right
        self.PWMmoterPin3 = machine.PWM(self.moterPin3)
        self.PWMmoterPin3.freq(400)
        self.PWMmoterPin3.duty_u16(3277)

        self.moterPin4 = machine.Pin(13)  # FR - front right
        self.PWMmoterPin4 = machine.PWM(self.moterPin4)
        self.PWMmoterPin4.freq(400)
        self.PWMmoterPin4.duty_u16(3277)

        self.motorPitch = 0
        self.motorRoll = 0
        self.motorThrottle = 0
        self.motorYaw = 0
        self.motor1_pwm = 0
        self.motor2_pwm = 0
        self.motor3_pwm = 0
        self.motor4_pwm = 0

    def motorProcessing(self, throttle, roll_correction, pitch_correction, yaw_correction):
        self.motorPitch = pitch_correction
        self.motorRoll = roll_correction
        self.motorThrottle = throttle
        self.motorYaw = yaw_correction

    def motorMixing(self):
        # X configuration motor mixing matrix
        # each motor receives throttle base plus signed corrections for each axis
        self.motor1_pwm = self.motorThrottle + self.motorRoll + self.motorPitch + self.motorYaw  # FL: +roll +pitch +yaw
        self.motor2_pwm = self.motorThrottle + self.motorRoll - self.motorPitch - self.motorYaw  # BL: +roll -pitch -yaw
        self.motor3_pwm = self.motorThrottle - self.motorRoll - self.motorPitch + self.motorYaw  # BR: -roll -pitch +yaw
        self.motor4_pwm = self.motorThrottle - self.motorRoll + self.motorPitch - self.motorYaw  # FR: -roll +pitch -yaw

        if self.motorThrottle < 1050:
            # safety cutoff - force all motors to minimum when throttle below threshold
            self.PWMmoterPin1.duty_u16(3277)
            self.PWMmoterPin2.duty_u16(3277)
            self.PWMmoterPin3.duty_u16(3277)
            self.PWMmoterPin4.duty_u16(3277)
        else:
            # clamp output to valid ESC range: 3277=1ms minimum, 6554=2ms maximum at 400Hz on 16-bit register
            self.PWMmoterPin1.duty_u16(max(3277, min(6554, pwm.PWMmap(self.motor1_pwm))))
            self.PWMmoterPin2.duty_u16(max(3277, min(6554, pwm.PWMmap(self.motor2_pwm))))
            self.PWMmoterPin3.duty_u16(max(3277, min(6554, pwm.PWMmap(self.motor3_pwm))))
            self.PWMmoterPin4.duty_u16(max(3277, min(6554, pwm.PWMmap(self.motor4_pwm))))


class PWM:
    def __init__(self):
        # RC input range 1000-2000 maps to PWM duty cycle 3277-6554
        # 3277 = 1ms pulse width, 6554 = 2ms pulse width at 400Hz on Pico 16-bit PWM register
        self.inMin = 1000
        self.inMax = 2000
        self.outMin = 3277
        self.outMax = 6554

    def PWMmap(self, motor):
        # linear interpolation from RC range to PWM duty cycle range
        return int((motor - self.inMin) * (self.outMax - self.outMin) / (self.inMax - self.inMin) + self.outMin)


# test mode flags - set HAND_TEST True to lock throttle at minimum for bench testing
HAND_TEST = False
TEST_AXIS = "all"  # restrict corrections to single axis: "roll", "pitch", "yaw", or "all"
IMU_TEST = False

# instantiate all system objects
pwm = PWM()
droneIMU = imu()
droneTOF = tof()

# position hold PID gains - set to zero until optical flow tuning is complete
flowRollPID  = PID(0.03, 0.0001, 0.001)
flowPitchPID = PID(0.03, 0.0001, 0.001)

# attitude PID gains - determined through iterative roll rig testing
rollPID  = PID(1, 0.002, 0.1)
pitchPID = PID(1.2, 0.002, 0.1)
hightPID = PID(0.2, 0.0, 0.01)   # altitude hold PID
yawPID   = PID(0.5, 0.0, 0.0)

droneFlow = opticalFlow()
posHold   = positionHold(droneFlow, flowRollPID, flowPitchPID)

output     = motor()
controller = remote()

roll_correction  = 0.0
pitch_correction = 0.0
yaw_correction   = 0.0

rollTrim  = 0    # software trim offsets to compensate for IMU mounting offset and centre of mass imbalance
pitchTrim = 1.3

target_height    = 0
height_correction = 0.0

telemetry_counter = 0
loop_time = 0

# main control loop - busy wait enforces 100Hz rate (10000 microsecond cycle)
# busy wait used instead of sleep to avoid MicroPython scheduler timing jitter
while True:

    loop_start = time.ticks_us()

    controller.DataParse()          # read RC receiver input
    droneIMU.readIMU()              # read raw accelerometer and gyroscope
    droneTOF.readDistance()         # read TOF altitude
    droneIMU.readAccell()           # remap accelerometer axes
    droneIMU.accellCal()            # apply scaling
    droneIMU.accellAngles()         # calculate roll and pitch from gravity vector
    droneIMU.readGyro()             # remap gyroscope axes
    droneIMU.gyroCal()              # subtract bias offsets
    droneIMU.gyroAngle()            # integrate gyroscope rate to angle
    droneIMU.complimentoryFilter()  # fuse accelerometer and gyroscope estimates

    roll_raw = controller.roll - 1500   # centre stick around zero
    if abs(roll_raw) < 20:
        roll_raw = 0                    # apply deadband to prevent drift from stick centre noise

    pitch_raw = -(controller.pitch - 1500)  # invert pitch - forward stick commands nose down
    if abs(pitch_raw) < 20:
        pitch_raw = 0

    # combine stick input with calibration offset to produce target angle
    stick_target_roll  = roll_raw  * 0.04 + droneIMU.calibRoll  + rollTrim
    stick_target_pitch = pitch_raw * 0.04 + droneIMU.calibPitch + pitchTrim

    target_r = stick_target_roll
    target_p = stick_target_pitch

    # activate position hold only when armed and above minimum altitude
    if controller.arming > 1400 and droneTOF.hight > 50:
        flow_roll, flow_pitch = posHold.process(droneIMU.XGcal, droneIMU.YGcal)
        target_r += flow_roll   # outer position loop adds correction angle to inner attitude target
        target_p += flow_pitch

    if HAND_TEST:
        # bench test mode - runs PID and motors but throttle locked at 1000
        roll_correction  = rollPID.computePID(target_r,  droneIMU.finalRoll,  droneIMU.XGcal)
        pitch_correction = pitchPID.computePID(target_p, droneIMU.finalPitch, droneIMU.YGcal)
        yaw_correction   = (controller.yaw - 1500) * 0.1
        output.motorProcessing(1000, roll_correction, pitch_correction, 0)
        output.motorMixing()
        print(f"AccelRoll:{droneIMU.ARdegrees:+6.1f}° AccelPitch:{droneIMU.APdegrees:+6.1f}°")
        time.sleep(0.2)
    else:
        if controller.arming > 1400:  # arming switch active
            if controller.throttle <= 1050:
                # reset all PID state when throttle at minimum - prevents accumulated error from previous flight
                rollPID.reset()
                pitchPID.reset()
                yawPID.reset()
                hightPID.reset()
                flowRollPID.reset()
                flowPitchPID.reset()
                height_correction = 0.0
                target_height = 0
            else:
                # capture target height on first valid altitude reading after arming
                if target_height <= 0 and droneTOF.hight > 30:
                    target_height = droneTOF.hight
                elif target_height > 0:
                    throttle_input = controller.throttle - 1500
                    if abs(throttle_input) > 50:
                        target_height += throttle_input * 0.001  # allow pilot to adjust target altitude via throttle stick

                roll_correction  = rollPID.computePID(target_r, droneIMU.finalRoll,  droneIMU.XGcal)
                pitch_correction = pitchPID.computePID(target_p, droneIMU.finalPitch, droneIMU.YGcal)
                if droneTOF.hight > 30:
                    height_correction = hightPID.computePID(target_height, droneTOF.hight)
                else:
                    height_correction = 0.0  # disable altitude hold below 30mm to prevent ground interference

            yaw_raw = controller.yaw - 1500
            if abs(yaw_raw) < 20:
                yaw_raw = 0  # deadband on yaw stick
            yaw_correction = yawPID.computePID(yaw_raw * 0.1, droneIMU.ZGcal)

            # TEST_AXIS allows isolating individual axes during tuning
            if TEST_AXIS == "roll":
                output.motorProcessing(controller.throttle, roll_correction, 0, 0)
                output.motorMixing()
            elif TEST_AXIS == "pitch":
                output.motorProcessing(controller.throttle, 0, pitch_correction, 0)
                output.motorMixing()
            elif TEST_AXIS == "yaw":
                output.motorProcessing(controller.throttle, 0, 0, yaw_correction)
                output.motorMixing()
            else:
                # full flight mode - all axes active, altitude correction added to throttle
                output.motorProcessing(controller.throttle + height_correction, roll_correction, pitch_correction, yaw_correction)
                output.motorMixing()

        else:
            # disarmed - force all motors to minimum and reset all PID state
            output.PWMmoterPin1.duty_u16(3277)
            output.PWMmoterPin2.duty_u16(3277)
            output.PWMmoterPin3.duty_u16(3277)
            output.PWMmoterPin4.duty_u16(3277)
            rollPID.reset()
            pitchPID.reset()
            yawPID.reset()
            hightPID.reset()
            flowRollPID.reset()
            flowPitchPID.reset()
            target_height = 0
            roll_correction  = 0.0
            pitch_correction = 0.0
            yaw_correction   = 0.0
            height_correction = 0.0
            print("disarmed")

    loop_time = time.ticks_diff(time.ticks_us(), loop_start)

    # transmit telemetry every 10th loop = 10Hz to avoid overloading the WiFi stack
    telemetry_counter += 1
    if telemetry_counter >= 10:
        telemetry_counter = 0
        try:
            telemetry = "T:{} H:{} Hc:{:.1f} Th:{} Roll:{:.1f} AccRoll:{:.1f} Pitch:{:.1f} Gx:{:.3f} Gy:{:.3f} RawGx:{:.3f} RawPx:{:.3f} | Rc:{:.2f} Pc:{:.2f} Yaw:{} | Fdx:{:.2f} Fdy:{:.2f} | M1:{:.0f} M2:{:.0f} M3:{:.0f} M4:{:.0f} | Loop:{}us".format(
                controller.throttle, droneTOF.hight, height_correction, target_height,
                droneIMU.finalRoll, droneIMU.ARdegrees, droneIMU.finalPitch,
                droneIMU.XGcal, droneIMU.YGcal,
                droneIMU.Xg - droneIMU.gyroXbias,
                droneIMU.Yg - droneIMU.gyroYbias,
                roll_correction, pitch_correction, controller.yaw,
                posHold.last_dx, posHold.last_dy,
                output.motor1_pwm, output.motor2_pwm, output.motor3_pwm, output.motor4_pwm,
                loop_time
            )
            sock.sendto(telemetry.encode(), (target_ip, target_port))
            print(telemetry)
        except Exception as e:
            print(f"Telemetry error: {e}")

    # busy wait to complete 10000 microsecond cycle - maintains consistent 100Hz loop rate
    while time.ticks_diff(time.ticks_us(), loop_start) < 10000:
        pass
