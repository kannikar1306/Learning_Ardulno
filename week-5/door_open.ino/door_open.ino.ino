#include <ESP32Servo.h>
Servo myServo;
char status = 'C';


void setup() {
  Serial.begin(9600);
  myServo.attach(32);  // ต่อ servo ที่ขา 32
}

void loop() {
  if (Serial.available() > 0) {
    char status_read = Serial.read();  // อ่านค่าจากมุม python
    if (status_read != status) {
      status = status_read;
    }

    if(status == 'C'){
      myServo.write(0);
      printf("close the Door\n");
    }else if (status == 'O'){
      myServo.write(90);
      printf("Open the Door\n");
    }
  }
}

