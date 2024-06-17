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

const int slowness = 6;   //slowness factor, ms wait between 1deg movements, change to set speed

const int servoPin1 = 5;// nano pwm 3 5 6 9 10 11
const int servoPin2 = 9;
const int servoPin3 = 6;
const int servoPin4 = 10;

//Pi2 will communicate on digital input pins
const int Ard2out_neopix = 2;
const int Pi2Pin_notdef = 4;
const int Pi2Pin_door3 = 7;
const int Pi2Pin_door4 = 8;

//door angles
const int CLOSE_DOOR1 = 179;
const int OPEN_DOOR1 = 129;
const int CLOSE_DOOR2 = 5;
const int OPEN_DOOR2 = 50;
const int CLOSE_DOOR3 = 10;
const int OPEN_DOOR3 = 68;
const int CLOSE_DOOR4 = 175;
const int OPEN_DOOR4 = 130;

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
  Serial.begin(9600);
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo3.attach(servoPin3);
  servo4.attach(servoPin4);
 
  pinMode(Ard2out_neopix, OUTPUT);
  pinMode(Pi2Pin_notdef, INPUT);
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
    digitalWrite(Ard2out_neopix, LOW);
  }
  if (receivedChar=='2')
  {
    digitalWrite(Ard2out_neopix, HIGH);
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
