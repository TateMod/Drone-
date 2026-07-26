#ifndef Biquad_HPP
#define Biquad_HPP


class Biquadfilter{
    public:
        Biquadfilter(float cutoff_hz, float sample_hz);

        float update(float x);
        void reset();

    private:

    //Does anything need this value again after this one calculation finishes
    float b0 ;
    float b1 ;
    float b2 ;
    float a1 ;
    float a2 ; 
    float x1 = 0;
    float x2 = 0;
    float y1 = 0;
    float y2 = 0;

}; 
#endif