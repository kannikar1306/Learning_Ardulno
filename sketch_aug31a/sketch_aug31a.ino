#include <ESP32Servo.h>
Servo myServo;


void setup() {
  Serial.begin(9600);  // put your setup code here, to run once:
  myServo.attach(32);
}

void loop() {
  if (Serial.available() > 0) {
    String angle = Serial.readStringUntil('\n');
    angle.trim();
    //Serial.print(angle);
    if (angle == "C") {
      myServo.write(0);
      Serial.print("0");
    } else if (angle =="10") {
      myServo.write(10);
      Serial.print("10");
    } else if (angle =="20") {
      myServo.write(20);
      Serial.print("20");
    } else if (angle =="30") {
      myServo.write(30);
      Serial.print("30");
    } else if (angle =="40") {
      myServo.write(40);
      Serial.print("40");
    } else if (angle =="50") {
      myServo.write(50);
      Serial.print("50");
    } else if (angle =="60") {
      myServo.write(60);
      Serial.print("60");
    } else if (angle =="70") {
      myServo.write(70);
      Serial.print("70");
    } else if (angle =="80") {
      myServo.write(80);
      Serial.print("80");
    } else if (angle =="90") {
      myServo.write(90);
      Serial.print("90");
    }
  }
  }
