char receivedChar;
boolean newData = false;
#include<Servo.h>
Servo servo1;     // Servo 1 = door1
#include<Servo.h>
Servo servo2;     // Servo 2 = door2
#include<Servo.h>
Servo servo3;     // Servo 3 = door3
#include<Servo.h>
Servo servo4;     // Servo 4 = door4 
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
Adafruit_NeoPixel pixels1(8, 2, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels2(8, 3, NEO_GRB + NEO_KHZ800);

const int slowness = 6;   //slowness factor, ms wait between 1deg movements, change to set speed

const int servoPin1 = 5;// nano pwm 3 5 6 9 10 11
const int servoPin2 = 6;
const int servoPin3 = 9;
const int servoPin4 = 10;

//Pi2 will communicate on digital input pins
const int Pi2Pin_neopix = 4;
const int Pi2Pin_door3 = 7;
const int Pi2Pin_door4 = 8;
boolean light2_dig_const_flag = false;

//door angles
const int CLOSE_DOOR1 = 179;
const int OPEN_DOOR1 = 129;
const int CLOSE_DOOR2 = 5;
const int OPEN_DOOR2 = 50;
const int CLOSE_DOOR3 = 10;
const int OPEN_DOOR3 = 68;
const int CLOSE_DOOR4 = 175;
const int OPEN_DOOR4 = 120;

int pos1_current = OPEN_DOOR1; //initial position variables for servos
int pos1_target = OPEN_DOOR1;
int pos2_current = OPEN_DOOR2; //initial position variables for servos
int pos2_target = OPEN_DOOR2;
int pos3_current = OPEN_DOOR3; //initial position variables for servos  >
int pos3_target = OPEN_DOOR3;
int pos4_current = OPEN_DOOR4; //initial position variables for servos
int pos4_target = OPEN_DOOR4;

void setup() 
{
  #if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
    clock_prescale_set(clock_div_1);
  #endif
  Serial.begin(9600);
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo3.attach(servoPin3);
  servo4.attach(servoPin4);
 
  pixels1.begin();
  pixels2.begin();
  pinMode(Pi2Pin_neopix, INPUT);
  pinMode(Pi2Pin_door3, INPUT);
  pinMode(Pi2Pin_door4, INPUT);
}

void loop() 
{
  recvInfo();
  moveServo();
}

void recvInfo() 
{
  if (Serial.available() > 0) 
  {
    receivedChar = Serial.read();
    Serial.println(receivedChar);    
  }  
}
void moveServo() 
{
  //target commands
  if (receivedChar=='a')
  {
    pos1_target=OPEN_DOOR1;
  }
  if (receivedChar=='b') 
  {
    pos1_target=CLOSE_DOOR1;
  }
  if (receivedChar=='c')
  {
    pos2_target=OPEN_DOOR2;
  }
  if (receivedChar=='d') 
  {
    pos2_target=CLOSE_DOOR2;
  }
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
  if ((digitalRead(Pi2Pin_neopix) == LOW) && (light2_dig_const_flag)) 
  {
    pixels2.clear();
    pixels2.show();
    light2_dig_const_flag=false;
  }
  if ((digitalRead(Pi2Pin_neopix) == HIGH) && (!light2_dig_const_flag)) 
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
    light2_dig_const_flag=true;
  }
//DOOR 3 Pi2 control
  if ((digitalRead(Pi2Pin_door3) == HIGH)) 
  {
      pos3_target=OPEN_DOOR3;
  }
  else 
  {
      pos3_target=CLOSE_DOOR3;
  }
  //DOOR 4 Pi2 control
  if ((digitalRead(Pi2Pin_door4) == HIGH)) 
  {
      pos4_target=OPEN_DOOR4;
  }
  else 
  {
      pos4_target=CLOSE_DOOR4;
  }
  
  //movement
  if (pos1_current<pos1_target) //SERVO 1
  {
    pos1_current=pos1_current+1;
    servo1.write(pos1_current);     
    delay(slowness); 
  }
  if (pos1_current>pos1_target)
  {
    pos1_current=pos1_current-1;
    servo1.write(pos1_current);     
    delay(slowness); 
  }
  if (pos2_current<pos2_target) //SERVO 2
  {
    pos2_current=pos2_current+1;
    servo2.write(pos2_current);     
    delay(slowness); 
  }
  if (pos2_current>pos2_target)
  {
    pos2_current=pos2_current-1;
    servo2.write(pos2_current);     
    delay(slowness); 
  }
  if (pos3_current<pos3_target) //SERVO 3
  {
    pos3_current=pos3_current+1;
    servo3.write(pos3_current);     
    delay(slowness); 
  }
  if (pos3_current>pos3_target)
  {
    pos3_current=pos3_current-1;
    servo3.write(pos3_current);     
    delay(slowness); 
  }
  if (pos4_current<pos4_target) //SERVO 4
  {
    pos4_current=pos4_current+1;
    servo4.write(pos4_current);     
    delay(slowness); 
  }
  if (pos4_current>pos4_target)
  {
    pos4_current=pos4_current-1;
    servo4.write(pos4_current);     
    delay(slowness); 
  }
}
