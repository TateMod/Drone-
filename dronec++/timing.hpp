#ifndef TIMING_HPP
#define TIMING_HPP

#include <cstdint>

 class timing {

    public:
        void start_loop();
        void end_loop();
        float loop_time;
    private:
        uint64_t start;
        uint64_t end;
       




};
#endif