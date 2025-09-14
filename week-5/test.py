import face_recognition
import cv2
import serial
import time
import numpy as np

# -------------------------------
# ตั้งค่า Serial Port ไปยัง Arduino
# -------------------------------
arduino = serial.Serial('COM3', 9600, timeout=1)  
time.sleep(2)

# -------------------------------
# เปิดกล้อง
# -------------------------------
video_capture = cv2.VideoCapture(0)

print("👉 มองกล้องเพื่อบันทึกใบหน้าผู้มีสิทธิ์")
authorized_encoding = None

# บันทึกใบหน้าผู้มีสิทธิ์จากกล้องครั้งแรก
while authorized_encoding is None:
    ret, frame = video_capture.read()
    if not ret:
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if len(face_encodings) > 0:
        authorized_encoding = face_encodings[0]
        print("✅ เก็บใบหน้าผู้มีสิทธิ์แล้ว")
        time.sleep(1)
        break

# -------------------------------
# เริ่มตรวจจับทุกเฟรม
# -------------------------------
while True:
    ret, frame = video_capture.read()
    if not ret:
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        match = face_recognition.compare_faces([authorized_encoding], face_encoding, tolerance=0.5)[0]

        if match:
            name = "AUTHORIZED"
            print("✅ Authorized face detected → Door Open")
            arduino.write(b'O')  # เปิด
            color = (0, 255, 0)
        else:
            name = "UNKNOWN"
            print("❌ Unauthorized face detected → Door Locked")
            arduino.write(b'C')  # ล็อก
            color = (0, 0, 255)

        # กรอบใบหน้า
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        # ชื่อที่มุมซ้ายล่าง
        cv2.putText(frame, name, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

video_capture.release()
cv2.destroyAllWindows()
