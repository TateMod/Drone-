
#include <cmath>
#include "Biquad.hpp"
#include <math.h>



Biquadfilter::Biquadfilter(float cutoff_hz,float sample_hz){
  constexpr float PI_F = 3.14159265358979323846f;
  float w = 2 * PI_F * cutoff_hz / sample_hz;
  float q = 0.707;
  float k = std::tan(w/2);
  float norm = 1 / (1+k/q+k*k);
  b0 = k*k*norm ;
  b1 = 2* b0;
  b2 = b0;

  a1 = 2 *(k *k -1) * norm ;
  a2 = (1 - k / q + k * k) * norm;
  x1 = x2 = 0.0;
  y1 = y2 = 0.0;

}




float Biquadfilter::update(float x)
{

    float y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;



    x2 = x1;
    x1 = x;
    y2 = y1;
    y1 = y;
return y;
}

void Biquadfilter::reset(){

    x1 = 0.0;
    x2 = 0.0;
    y1 =0.0;
    y2 = 0.0;


}