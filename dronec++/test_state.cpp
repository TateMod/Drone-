
           
#include "test_state.hpp"
#include "Remote.hpp"   // need full definitions here since we use their members/functions
#include "Motor.hpp"



         test_state :: test_state(int test):test(test){
            


         }
         void  test_state :: what_test(Remote& controller, Motor& output,
                             float roll_correction, float pitch_correction,
                             float yaw_correction, float height_correction){

            if (test == 1){//ROL
                output.motorProcessing(controller.getThrottle(), -roll_correction, 0, 0);
                output.motorMixing();
            }
            else if(test == 2){//PITCH
                output.motorProcessing(controller.getThrottle(), 0, pitch_correction, 0);
                output.motorMixing();

            }
            else if(test == 3){
                //YAW
                output.motorProcessing(controller.getThrottle(), 0, 0, yaw_correction);
                output.motorMixing();
            }
            else if (test == 4){

                output.motorProcessing(controller.getThrottle(), -roll_correction, pitch_correction, yaw_correction);
                output.motorMixing();

            


            }else{

                    // all
                output.motorProcessing(controller.getThrottle() + height_correction, -roll_correction, pitch_correction, yaw_correction);
                output.motorMixing();

            }

         }

   