
#include "Remote.hpp"
#include <hardware/uart.h>
#include <hardware/gpio.h>
#include <cstdlib>

Remote::Remote() {
    uart_init(uart0, 115200);
    gpio_set_function(1, GPIO_FUNC_UART);
}

void Remote::DataParse() {
    while (uart_is_readable(uart0)) {
        uint8_t header = uart_getc(uart0);

        if (header == 0x20) {
            uint8_t second_byte = uart_getc(uart0);

            if (second_byte == 0x40) {
                uint8_t rest[30];
                for (int i = 0; i < 30; i++) {
                    rest[i] = uart_getc(uart0);
                }

                for (int i = 0; i < 28; i += 2) {
                    int value = (rest[i + 1] * 256) + rest[i];
                    channels[i / 2] = value;
                }

                roll = channels[0];
                pitch = channels[1];
                yaw = channels[3];
                if (channels[2] >= 1000 && channels[2] <= 2000) {
                    throttle = channels[2];
                }
                arming = channels[4];
            }
        }
    }
}

void Remote::rcProcessing() {
    int roll_raw = roll - 1500;
    if (std::abs(roll_raw) < 20.0f){
        roll_raw = 0;
    }
    int pitch_raw = pitch - 1500;
    if (std::abs(pitch_raw) < 20.0f){
        pitch_raw = 0;
    }
    
    int yaw_raw = yaw - 1500;
    if (std::abs(yaw_raw) < 20.0f){
        yaw_raw = 0;}



    target_r  = roll_raw  * 0.04f ;//+ rollTrim if wann add trim
    target_p = pitch_raw * 0.04f;// + pitchTrim
    target_y = yaw_raw * 0.1f;// sacling factor







}