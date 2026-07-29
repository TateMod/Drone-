#include "timing.hpp"
#include <hardware/timer.h>

void timing::start_loop() {
    start = time_us_64();


}

void timing:: end_loop(){
end = time_us_64();
       loop_time =(float) (end - start) / 1e6f;
}