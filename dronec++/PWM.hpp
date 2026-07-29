#ifndef PWM_HPP
#define PWM_HPP
#include <array>
#include <cstdint>



class PWM {
public:
    PWM();          // like constructure but for whle thing
                               // function declared but donest taeka nything in
    int PWMmap(float motor);

    



private:
    int inMin = 1000;
    int inMax = 2000;
    int outMin = 3277;
    int outMax = 6554;




};
#endif