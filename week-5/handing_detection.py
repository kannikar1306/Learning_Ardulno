import cv2  # opencv
import mediapipe as mp
import math
import serial
import time

# ====== CONFIG ======
COM_PORT = "COM3"  # เปลี่ยนตามเครื่อง
BAUDRATE = 9600
EMA_ALPHA = 0.2  # smoothing 0-1 (สูง = ตอบสนองไว, แต่สั่น)
SHOW_LINES = True

# ====== Serial ======
ser = serial.Serial(COM_PORT, BAUDRATE, timeout=1)
time.sleep(2)


# ====== MediaPipe Pose ======
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


# ฟังก์ชั่นต่างๆ
def to_vec(a, b):
    return (b[0] - a[0], b[1] - a[1])


def angle_between(u, v):
    ux, uy = u
    vx, vy = v
    du = math.hypot(ux, uy)
    dv = math.hypot(vx, vy)
    if du == 0 or dv == 0:
        return None
    cos_t = (ux * vx + uy * vy) / (du * dv)
    # clamp numeric noise
    cos_t = max(-1.0, min(1.0, cos_t))
    return math.degrees(math.acos(cos_t))


# เรียกใช่
cap = cv2.VideoCapture(0)  # ดึงหน้าจอขึ้นมา
ema_angle = None

with mp_pose.Pose(
    model_complexity=1,  # with ตำแหน่งแรก
    enable_segmentation=False,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
) as pose:

    while True:  # while ตำแหน่งที่สอง
        ok, frame = cap.read()
        if not ok:
            continue
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)

        angle_0_90 = None
        if res.pose_landmarks:  # detec แบบสามมิติ
            lm = res.pose_landmarks.landmark

            # Get 2D points (pixel coords)
            def p(id):
                return (int(lm[id].x * w), int(lm[id].y * h))

            L_ELBOW, L_WRIST = p(mp_pose.PoseLandmark.LEFT_ELBOW), p(
                mp_pose.PoseLandmark.LEFT_WRIST
            )  # กำหนดขอบเขตซ้ายขวา
            R_ELBOW, R_WRIST = p(mp_pose.PoseLandmark.RIGHT_ELBOW), p(
                mp_pose.PoseLandmark.RIGHT_WRIST
            )

            # Forearm vectors: elbow -> wrist (camera plane)
            vL = to_vec(L_ELBOW, L_WRIST)
            vR = to_vec(R_ELBOW, R_WRIST)

            theta = angle_between(vL, vR)  # degrees 0..180 (in-plane)
            if theta is not None:
                # We want 0..90 max; if >90, reflect down (people may cross)
                theta = min(theta, 180 - theta)  # fold to [0,90]
                angle_0_90 = max(0, min(90, theta))

                # EMA smoothing ความสมูท
                if ema_angle is None:
                    ema_angle = angle_0_90
                else:
                    ema_angle = EMA_ALPHA * angle_0_90 + (1 - EMA_ALPHA) * ema_angle

                # Map to servo 0..180
                servo_deg = int(max(0, min(180, round(ema_angle * 2))))

                # Send to ESP32 (newline-terminated integer)ส่งค่าข้ามไปยัง
                ser.write(f"{servo_deg}\n".encode())

                # Draw UI การวาดข้อความ
                cv2.putText(
                    frame,
                    f"Angle: {angle_0_90:.1f} deg  |  Servo: {servo_deg}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )

                if SHOW_LINES:  # โชว์ตามนิ้วตามข้อต่างๆ
                    cv2.circle(frame, L_ELBOW, 6, (0, 255, 255), -1)
                    cv2.circle(frame, R_ELBOW, 6, (0, 255, 255), -1)
                    cv2.circle(frame, L_WRIST, 6, (255, 0, 255), -1)
                    cv2.circle(frame, R_WRIST, 6, (255, 0, 255), -1)
                    cv2.line(frame, L_ELBOW, L_WRIST, (0, 255, 255), 3)
                    cv2.line(frame, R_ELBOW, R_WRIST, (0, 255, 255), 3)

            mp_drawing.draw_landmarks(
                frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )
        cv2.imshow("Two-Arm Angle → Servo", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit ออกจากโปรแกรม
            break
