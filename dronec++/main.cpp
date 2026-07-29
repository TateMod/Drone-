#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/i2c.h"
#include "hardware/dma.h"
#include "hardware/watchdog.h"
#include "hardware/clocks.h"
#include "hardware/uart.h"

#include "PID.hpp"
#include "IMU.hpp"
#include "Motor.hpp"
#include "Remote.hpp"
#include "hight.hpp"
#include "Biquad.hpp"
#include "PWM.hpp"
#include "timing.hpp"
#include "test_state.hpp"
#include "MPU9250.hpp"
// check tof stiff later ned to pick a libary first


// SPI Defines
// We are going to use SPI 0, and allocate it to the following GPIO pins
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define SPI_PORT spi0
#define PIN_MISO 16
#define PIN_CS   17
#define PIN_SCK  18
#define PIN_MOSI 19

// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT i2c0
#define I2C_SDA 4
#define I2C_SCL 5


PWM pwm;
IMU droneIMU;
hight droneHight;
timing loopTimer;
Biquadfilter gyroFilter(30.0f, 100.0f);
test_state test(4);
//1 = roll
//2 = pitch
//3 = yaw
//4 = all no hight 
//else = all
MPU9250 IMUSensor(4, 5);
 
PID yawPID(0.5, 0.0, 0.0);
PID hightPID (1,0.01,0.2);
PID rollPID (1.2, 0.002, 0.2); // first ( 1.0, 0.002, 0.1 )
PID pitchPID(1.2, 0.002, 0.2);//1.2#d 0.2 -0.1 pretty goo i think

Motor output;
Remote controller;




//initilsing varabuls
float roll_correction = 0.0f;
float pitch_correction = 0.0f;
float yaw_correction  = 0.0f;
float hight_correction = 0.0f;



int main(){

    stdio_init_all();

    // SPI initialisation. This example will use SPI at 1MHz.
    spi_init(SPI_PORT, 1000*1000);
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_CS,   GPIO_FUNC_SIO);
    gpio_set_function(PIN_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    
    // Chip select is active-low, so we'll initialise it to a driven-high state
    gpio_set_dir(PIN_CS, GPIO_OUT);
    gpio_put(PIN_CS, 1);
    // For more examples of SPI use see https://github.com/raspberrypi/pico-examples/tree/master/spi

    // I2C Initialisation. Using it at 400Khz.
    i2c_init(I2C_PORT, 400*1000);
    
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA);
    gpio_pull_up(I2C_SCL);
    // For more examples of I2C use see https://github.com/raspberrypi/pico-examples/tree/master/i2c

    // Watchdog example code
    if (watchdog_caused_reboot()) {
        printf("Rebooted by Watchdog!\n");
        // Whatever action you may take if a watchdog caused a reboot
    }
    // Enable the watchdog, requiring the watchdog to be updated every 100ms or the chip will reboot
    // second arg is pause on debug which means the watchdog will pause when stepping through code
    watchdog_enable(100, 1);
    // You need to call this function at least more often than the 100ms in the enable call to prevent a reboot
    watchdog_update();



   
    while (true) {

        loopTimer.start_loop();
    
        controller.DataParse();       
    
        droneIMU.accellAngles();
        droneIMU.gyroAngles();
        droneIMU.complimentoryFilter();

        controller.rcProcessing();// new calss in remote

        if (controller.getArming() > 1400){
            if (controller.getThrottle() <= 1050){

            rollPID.reset();
            pitchPID.reset();
            yawPID.reset();

            roll_correction = 0.0;
            pitch_correction = 0.0;
            yaw_correction   = 0.0;

            }else{//need to cahked data types match

                //armed stuff
            float gx_val = IMUSensor.getgx();
            float gy_val = IMUSensor.getgy();
            float gz_val = IMUSensor.getgz();
            roll_correction = rollPID.computePID(controller.target_r,  droneIMU.getFinalRoll(),  &gx_val);//  XGcal       
            pitch_correction = pitchPID.computePID(  controller.target_p,  droneIMU.getFinalPitch(), &gy_val);//YGcal
            hight_correction = droneHight.hight_check( controller.getThrottle());
              // check YAW PID working as in real target?
            yaw_correction = yawPID.computePID(controller.target_y, gz_val,  nullptr);//ZGcal
        
           test.what_test(controller, output, roll_correction, pitch_correction, yaw_correction, hight_correction);

            }    
            } else{
         
            output.motorOFF();
           
            rollPID.reset();
            pitchPID.reset();
            yawPID.reset();

            roll_correction  = 0.0;
            pitch_correction = 0.0;
            yaw_correction   = 0.0;
            hight_correction = 0.0;


            }
        

      

      
            loopTimer.end_loop();
        }
    }

