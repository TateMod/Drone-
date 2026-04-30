An open-source sub-250g quadcopter UAV built on custom MicroPython firmware developed from first principles. The platform provides full access to flight control algorithms including PID attitude control, complementary filter sensor fusion, motor mixing, optical flow position hold and TOF altitude hold. Designed to be reproducible and accessible for learning and further development.

---

## Demo Video

[ADD VIDEO LINK HERE]

---

## Repository Structure

```
/firmware          - Pico W2 flight controller MicroPython source code
/companion         - Raspberry Pi Zero W2 telemetry and camera code
/schematics        - Wiring diagrams and circuit schematics (EasyEDA)
/frame             - 3D printable CAD frame files (STL and OnShape)
/docs              - Build guide and assembly documentation
```

---

## Components

### Computing
| Component | Purpose |
|---|---|
| Raspberry Pi Pico W2 | Flight controller — runs all flight algorithms |
| Raspberry Pi Zero W2 | Companion computer — telemetry logging and camera |

### Sensors
| Component | Purpose |
|---|---|
| Adafruit LSM9DS1 9-axis IMU | Attitude estimation (roll, pitch, yaw) |
| Adafruit VL53L1X Time of Flight | Altitude estimation |
| PMW3901 Optical Flow Sensor | Position hold assistance |
| Raspberry Pi Camera Module 3 | Camera feed via companion computer |

### Propulsion
| Component | Purpose |
|---|---|
| Flash 1404 4500KV motors (x4) | Generates adequate thrust for ~200g system |
| 3.5 inch tri-blade propellers (x4) | Tri-blade for stable efficient flight at lower speeds |
| HAKRC 45A 4-in-1 BLHeli_S ESC | Controls motor speed via PWM signals |

### Radio
| Component | Purpose |
|---|---|
| FlySky FS-iA6B RC receiver | Receives control commands via iBus |

### Power
| Component | Purpose |
|---|---|
| GNB 1100mAh 2S 60C LiHV LiPo battery | Powers the system |
| Pololu 5V 3A step-up/step-down voltage regulator | Regulates battery voltage to 5V for processors |
| XT30 connectors | Battery and ESC power connections |

### Camera Connection
- Raspberry Pi Camera Module 3
- 15-pin to 15-pin adapter
- 22-pin to 15-pin ribbon cable (required for Zero W2)

### Tools and Equipment Required
- 60W soldering iron
- Multimeter (for debugging and testing)
- Solder
- Signal wires
- Jumper wires
- Zip ties
- Electrical tape
- Allen keys
- Wire clippers
- AA batteries (for transmitter)
- MicroSD card and USB adapter

---

## Wiring

![Wiring Diagram](https://github.com/user-attachments/assets/42d7349a-6831-49ab-9f66-c21792ad766a)

Follow the diagram above for visual guidance on all connections.

### Interface Pin Assignments

| Interface | Protocol | Pins | Purpose |
|---|---|---|---|
| IMU (LSM9DS1) | I2C | SDA: GPIO 4, SCL: GPIO 5 | Attitude data |
| TOF (VL53L1X) | I2C | SDA: GPIO 4, SCL: GPIO 5 | Altitude data |
| Optical Flow (PMW3901) | SPI | MISO: GPIO 16, MOSI: GPIO 19, SCK: GPIO 18, CS: GPIO 17 | Position hold |
| RC Receiver (FS-iA6B) | UART | RX: GPIO 1 | Pilot inputs |
| Motor 1 (Front Left) | PWM | GPIO 11 | Motor speed |
| Motor 2 (Back Left) | PWM | GPIO 14 | Motor speed |
| Motor 3 (Back Right) | PWM | GPIO 12 | Motor speed |
| Motor 4 (Front Right) | PWM | GPIO 13 | Motor speed |
| Calibration Button | GPIO | GPIO 20 (GND on other pin) | Arm and calibrate |

---

## Assembly Guide

### 1. Power System

1. Heat soldering iron to operating temperature
2. Pre-tin the XT30 connector pads
3. Solder 12–14 AWG wires to the XT30 connector — red to positive (+), black to negative (−)
4. Add the capacitor to the ESC capacitor pads, leaving room for the main power wires
5. Solder the XT30 wires to the ESC positive and negative pads, ensuring secure connections
6. Plug in the battery and listen for the ESC power-up beep sequence to confirm correct wiring

### 2. Voltage Regulator

1. Solder ESC VOUT to the regulator VIN
2. Solder ESC GND to the regulator GND
3. The regulator 5V output will supply the Pico W2, Zero W2 and RC receiver

### 3. Motors

1. Cut motor wires to length from motor platform to ESC if required
2. Solder motors to ESC motor pads:
   - Front left and back right motors: clockwise configuration
   - Front right and back left motors: counter-clockwise configuration (swap any two motor wires to reverse direction)

### 4. ESC Signal Wires

1. Using the dual-sided connector supplied with the ESC, snip one end leaving bare wires
2. Solder signal wires to extend their length to reach the Pico W2 GPIO pins
3. Connect each signal wire to the corresponding GPIO pin listed in the pin assignments table above

### 5. Sensor Wiring (Without Pico Headers)

**I2C Bus (IMU and TOF - shared bus):**
- Join IMU SCL and TOF SCL together and solder to GPIO 5
- Join IMU SDA and TOF SDA together and solder to GPIO 4

**SPI (Optical Flow):**
- MISO -> GPIO 16
- MOSI -> GPIO 19
- SCK -> GPIO 18
- CS -> GPIO 17

**Sensor Power (3.3V and GND):**
- Run a red wire to the furthest sensor, cutting the wire casing at each intermediate sensor to branch a connection to 3.3V or VIN
- Repeat with a black wire for GND, branching to each sensor

**RC Receiver:**
- Snip a male jumper wire and solder to Pico W2 UART RX GPIO 1
- Connect the other end to the iBus slot on the receiver using the connector supplied with it

### 6. Power Rails for Processors

1. Create a 5V rail by soldering jumper wires directly to the Pico W2 VSYS and Zero W2 5V power pins
2. Solder a male header onto this 5V rail for the RC receiver
3. Create a GND rail by soldering jumper wires to the Pico W2 GND and Zero W2 GND pins
4. Solder a male header onto this GND rail for the RC receiver

### 7. Calibration Button

1. Solder two wires to the button
2. Connect one wire to GPIO 20 and the other to GND

### 8. With Pico Headers (Alternative)

- Solder female headers to the ends of signal wires connected to the Pico W2 and Zero W2
- For shared I2C bus wires, solder sensor wires together first and then add a single female header
- Ensure sufficient wire length to allow connections without strain

---

## Firmware Setup

### Pico W2 — Flight Controller

1. Hold the BOOTSEL button on the Pico W2 and connect via USB to enter bootloader mode
2. Download MicroPython V1.27.0 UF2 from the official Raspberry Pi website
3. Drag the UF2 file onto the Pico W2 drive that appears
4. Open Thonny IDE (version 4.1.7 or later)
5. Open the firmware files from the `/firmware` folder
6. Upload all files to the Pico W2 using Thonny
7. Run `main.py` — the drone will wait for the calibration button to be pressed before arming

### Zero W2 — Companion Computer

1. Insert a MicroSD card into your computer using a USB adapter
2. Open Raspberry Pi Imager
3. Select Raspberry Pi Zero 2 W as the device and Raspberry Pi OS Lite as the OS
4. Flash the SD card and insert into the Zero W2
5. Upload the companion computer files from the `/companion` folder

---

## PID Tuning Values

These are the final values used in testing. Adjust based on your build weight and component placement.

| Axis | P | I | D |
|---|---|---|---|
| Roll | 1.6 | 0.002 | 0.4 |
| Pitch | 2.0 | 0.002 | 0.4 |
| Yaw | 0.5 | 0.0 | 0.0 |
| Altitude | 0.2 | 0.0 | 0.01 |

---

## License

This project is published under the MIT License. All third-party libraries used in the firmware are distributed under permissive open-source licences (MIT and BSD) which permit use, modification and redistribution with attribution.
