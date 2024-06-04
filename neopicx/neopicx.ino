char receivedChar;
boolean newData = false;
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
Adafruit_NeoPixel pixels1(8, 2, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels2(8, 3, NEO_GRB + NEO_KHZ800);

//Pi2 will communicate on digital input pin through ard2
const int Ard2in_neopix = 4;
boolean light2_dig_cont_flag = false;

void setup() 
{
  Serial.begin(9600);
  #if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
  #endif
  pixels1.begin();
  pixels2.begin();
  pinMode(Ard2in_neopix, INPUT);
}

void loop() 
{
  recvInfo();
  lights();
}

void recvInfo() 
{
  if (Serial.available() > 0) 
  {
    receivedChar = Serial.read();
    Serial.println(receivedChar);    
  }  
}
void lights()
{
  //light switches
  
  if (receivedChar=='1')
  {
    pixels1.clear();
    pixels1.show();
  }
  if (receivedChar=='2')
  {
    pixels1.clear();
    pixels1.show();
    pixels1.setPixelColor(1, pixels1.Color(0, 0, 5));
    pixels1.setPixelColor(2, pixels1.Color(0, 0, 5));
    pixels1.setPixelColor(3, pixels1.Color(0, 0, 5));
    pixels1.setPixelColor(4, pixels1.Color(0, 0, 5));
    pixels1.setPixelColor(5, pixels1.Color(0, 0, 5));
    pixels1.setPixelColor(6, pixels1.Color(0, 0, 5));
    pixels1.setPixelColor(7, pixels1.Color(0, 0, 5));
    pixels1.setPixelColor(0, pixels1.Color(0, 0, 5));
    pixels1.show();
  }
  if ((digitalRead(Ard2in_neopix) == LOW) && (light2_dig_cont_flag)) 
  {
    pixels2.clear();
    pixels2.show();
    light2_dig_cont_flag=false;
    
  }
  if ((digitalRead(Ard2in_neopix) == HIGH) && (!light2_dig_cont_flag)) 
  {
    pixels2.clear();
    pixels2.show();
    pixels2.setPixelColor(1, pixels2.Color(0, 0, 5));
    pixels2.setPixelColor(2, pixels2.Color(0, 0, 5));
    pixels2.setPixelColor(3, pixels2.Color(0, 0, 5));
    pixels2.setPixelColor(4, pixels2.Color(0, 0, 5));
    pixels2.setPixelColor(5, pixels2.Color(0, 0, 5));
    pixels2.setPixelColor(6, pixels2.Color(0, 0, 5));
    pixels2.setPixelColor(7, pixels2.Color(0, 0, 5));
    pixels2.setPixelColor(0, pixels2.Color(0, 0, 5));
    pixels2.show();
    light2_dig_cont_flag=true;
  }
}
