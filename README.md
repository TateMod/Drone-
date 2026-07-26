CURRENTLY WORK IN PROGRESS

An open-source sub-250g quadcopter UAV built on custom MicroPython and c++ firmware developed from first principles. The platform provides full access to flight control algorithms including PID attitude control, complementary filter sensor fusion, motor mixing, optical flow position hold and TOF altitude hold. Designed to be reproducible and accessible for learning and further development.

---

## pictures

## Demo Videos

Not at testing stage

---

## Repository Structure

```
/firmware          - Pico W2 flight controller C++ source code
/schematics        - Wiring diagrams and circuit schematics (EasyEDA)
/frame             - 3D printable CAD frame files (STL and OnShape)
/docs              - Build guide and assembly documentation
```

---












## Components

### Computing
| Component | Purpose |
|---|---|
| Raspberry Pi Pico W2 | Flight controller - runs all flight algorithms |
| Raspberry Pi Zero W2 | Companion computer - telemetry logging and camera |

### Sensors
| Component | Purpose |
|---|---|
| | Attitude estimation (roll, pitch, yaw) with barometerand tempuature sensor for altatude estimation |
| Adafruit VL53L1X Time of Flight | Altitude estimation |
| PMW3901 Optical Flow Sensor | Position hold assistance |

### Propulsion
| Component | Purpose |
|---|---|
| Flash 1404 4500KV motors (x4) | Generates adequate thrust for ~200g system |
| 3 inch tri-blade propellers (x4) | Tri-blade for stable efficient flight at lower speeds |
| HAKRC 45A 4-in-1 BLHeli_S ESC | Controls motor speed via PWM signals |

### Radio
| Component | Purpose |
|---|---|
| FlySky FS-i6 6CH Transmitter & FS-X6B iBUS Receiver | Receives control commands via iBus |

### Power
| Component | Purpose |
|---|---|
| GNB 850mAh 3S 120C LiHV LiPo battery | Powers the system |
|  5V 3A step-up/step-down voltage regulator | Regulates battery voltage to 5V for processors |
| XT30 connectors | Battery and ESC power connections |
|  2S and 3s LiPo Charger | Charges the LiPo battery |

### Camera
| Component | Purpose |
|---|---|
|  | Camera feed via companion computer |
| 15-pin to 15-pin adapter | Connects camera to Zero W2 |
| 22-pin to 15-pin ribbon cable | Required for Zero W2 camera connection |

### Tools and Equipment Required
- 60W soldering iron
- Multimeter
- Solder
- Jumper wires
- Zip ties
- Electrical tape
- Allen keys
- Wire clippers
- AA batteries (for transmitter)
- MicroSD card and USB adapter
- 3d printer and PLA or PETG


## Bill of Materials


| Component | Price | Link |
|---|---|---|
| Raspberry Pi Pico W2 | £6.70 | [Buy](https://thepihut.com/products/raspberry-pi-pico-2-w) |
| Raspberry Pi Zero W2 | £14.40 | [Buy](https://thepihut.com/products/raspberry-pi-zero-2) |
| Adafruit VL53L1X TOF | £14.40 | [Buy](https://thepihut.com/products/adafruit-vl53l1x-time-of-flight-distance-sensor-30-to-4000mm-stemma-qt-qwiic) |
| PMW3901 Optical Flow Sensor | £6 | [Buy](https://www.aliexpress.com/item/1005011822845593.html) |
| 5V Buck Converter (step-down) | £2.15| [Buy](https://www.aliexpress.com/item/1005008257960729.html) |
| MPU9250+BMP280 GY-91 10DOF IMU | £4.69 | [Buy](https://www.aliexpress.com/item/1005002956541258.html) |
| Flash 1404 4500KV motors (x4) | £13.29 each (×4 = £53.16) | [Buy](https://www.unmannedtechshop.co.uk/products/flyfish-flash-1404-4500kv-fpv-motor) |
| HAKRC 45A 4-in-1 BLHeli_S ESC | £38.95 | [Buy](https://yourfpv.co.uk/product/hakrc-8-bit-45a-twin-mount-30-530-5mm-and-2020mm-4in1-esc/) |
| XT30 connectors | £5.99 | [Buy](https://www.amazon.co.uk/RUNCCI-Upgrade-Female-Connectors-Battery/dp/B07PC1YKVW) |
| FlySky FS-i6X Transmitter & FS-X6B Receiver | £68.00 | [Buy](https://www.flyingtech.co.uk/product/flysky-fs-i6x-10ch-transmitter-fs-x6b-2-4ghz-ibus-receiver/) |
| 15-pin to 15-pin camera adapter | £3.00 | [Buy](https://thepihut.com/products/raspberry-pi-zero-camera-adapter) |
| 22-pin to 15-pin ribbon cable | £1.70 | [Buy](https://thepihut.com/products/zero-camera-cable-joiner-for-raspberry-pi-22-pin-to-22-pin) |
| Jumper wires | £5.49 | [Buy](https://www.amazon.co.uk/Multicolored-Dupont-Breadboard-Compatible-Arduino/dp/B0DSZ7FD2V) |
| **Total** | **DRONE - 156** |**+ controller - 224.63** |













---

## Wiring

![Wiring Diagram](https://github.com/user-attachments/assets/880bb718-87af-4526-9794-92508a5a16d7)
Follow the diagram above for visual guidance on all connections.

### Interface Pin Assignments

| Interface | Protocol | Pins | Purpose |
|---|---|---|---|
| IMU (MPU9250)| I2C | SDA: GPIO 4, SCL: GPIO 5 | Attitude data |
| TOF (VL53L1X) | I2C | SDA: GPIO 4, SCL: GPIO 5 | Altitude data |
| Optical Flow (PMW3901) | SPI | MISO: GPIO 16, MOSI: GPIO 19, SCK: GPIO 18, CS: GPIO 17 | Position hold |
| RC Receiver (FS-iA6B) | UART | RX: GPIO 1 | Pilot inputs |
| Motor 1 (Front Left) | PWM | GPIO 11 | Motor speed |
| Motor 2 (Back Left) | PWM | GPIO 14 | Motor speed |
| Motor 3 (Back Right) | PWM | GPIO 12 | Motor speed |
| Motor 4 (Front Right) | PWM | GPIO 13 | Motor speed |


---

## Assembly Guide

### 1. Power System

1. Heat soldering iron to operating temperature
2. Pre-tin the XT30 connector pads
3. Solder 12–14 AWG wires to the XT30 connector - red to positive (+), black to negative (−)
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
2. Solder wires to extend their length to reach the Pico W2 GPIO pins
3. Connect each wire to the corresponding GPIO pin listed in the pin assignments table above

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

- Solder female headers to the ends of  wires connected to the Pico W2 and Zero W2
- For shared I2C bus wires, solder sensor wires together first and then add a single female header
- Ensure sufficient wire length to allow connections without strain

---

## Firmware Setup

### Pico W2 — Flight Controller

1 Install the Raspberry Pi Pico VS Code extension — easiest route, it bundles the SDK, toolchain (arm-none-eabi-gcc + riscv toolchain for RP2350), CMake, and Ninja for you automatically

### Zero W2 — Companion Computer

1. Insert a MicroSD card into your computer using a USB adapter
2. Open Raspberry Pi Imager
3. Select Raspberry Pi Zero 2 W as the device and Raspberry Pi OS Lite as the OS
4. Flash the SD card and insert into the Zero W2
5. Upload the companion computer files from the `/companion` folder

---

## PID Tuning Values

currently tuning on new rig

---

## License

This project is published under the MIT License. All third-party libraries used in the firmware are distributed under permissive open-source licences (MIT and BSD) which permit use, modification and redistribution with attribution.
