#include <ESP32Servo.h>
Servo myServo;


void setup() {
  Serial.begin(9600);  
  myServo.attach(32);  // ต่อ servo ที่ขา 32
}  

void loop() {
  if (Serial.available() > 0) {
    int angle = Serial.parseInt();  // อ่านค่าจากมุม python
    if (angle >= 0 && angle <= 90) {
      myServo.write(angle);
    }
  }
}
