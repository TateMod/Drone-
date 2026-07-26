#ifndef TEST_STATE_HPP
#define TEST_STATE_HPP
class Remote;   // forward declarations, avoids needing full includes here
class Motor;

class test_state{
    public:
        test_state(int test);// test numbers test for diff things
        void what_test(Remote& controller, Motor& output,
                        float roll_correction, float pitch_correction,
                        float yaw_correction, float height_correction);

    private:
        int test;






};
#endif