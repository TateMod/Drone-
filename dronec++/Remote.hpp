
#ifndef REMOTE_HPP
#define REMOTE_HPP
#include <array>

class Remote{
    
    
    public:
        Remote();
        void DataParse();
        //uart
        void rcProcessing();
        
        float target_r, target_p, target_y;
        // these can be called from anywhere in teh code with remote.___
        int getThrottle() const { return throttle; }//throttle getter fucntion
        int getArming() const { return arming; }

    
    private:
        std::array<int, 5> channels;
        int roll = 1500;
        int pitch = 1500;
        int throttle = 1000;
        int yaw = 1500;
        int arming = 0;
        bool uart_is_radabul = false;




    






};
#endif