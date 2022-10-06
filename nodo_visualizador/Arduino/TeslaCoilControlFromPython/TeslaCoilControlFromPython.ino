const int transistorONOFF = 4;
const int servoGainPIN = 5;
const int servoFreqPIN = 6;

#include <pyduino_bridge.h>

#include <Servo.h>

Servo servoGain;
Servo servoFreq;

//Create the Bridge_ino object for communication with Python
Bridge_ino myBridge(Serial);

void setup(){

  pinMode (transistorONOFF, OUTPUT);

  servoGain.attach(servoGainPIN);
  servoFreq.attach(servoFreqPIN);

  delay(500);

  // initialize the serial object
  Serial.begin(115200);

  // reset the Tesla Coil state
  digitalWrite (transistorONOFF, 0);
  servoGain.write(180);
  servoFreq.write(180);
}

void loop(){

  myBridge.read();

  const char* tagName = myBridge.headerOfMsg; // the header characters received from Python
  int intRecvd = myBridge.intsRecvd[0]; // the first int number received from Python
  int floatRecvd = int(myBridge.floatsRecvd[0]); // the first float number received from Python

  if(strcmp(tagName, "COIL") == 0){

    digitalWrite (transistorONOFF, intRecvd);

  }else if(strcmp(tagName, "DATA") == 0){
    // range 180 - 0 ( 180 min, 0 max )
    servoGain.write(intRecvd);
    servoFreq.write(floatRecvd);
  }

  // -------------------------------------------------------------
  // tell python we are ready [ IMPORTANT!!! DO NOT DELETE!!! ]
  if(millis()%1000 == 0){
    Serial.println("<Arduino is ready>");
  }
  // -------------------------------------------------------------

}
