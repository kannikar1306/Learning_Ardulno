import cv2
import mediapipe as mp
import math
import serial
import time

# ====== CONFIG ======
COM_PORT = "COM3"   # แก้เป็นพอร์ตจริง เช่น COM4 หรือ /dev/ttyUSB0
BAUDRATE = 9600
EMA_ALPHA = 0.2     # smoothing
SHOW_POINTS = True

# ====== Serial ======
ser = serial.Serial(COM_PORT, BAUDRATE, timeout=1)
time.sleep(2)  # รอ Arduino reset

# ====== MediaPipe Hands ======
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def calc_angle(v1, v2):
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    if mag1 * mag2 == 0:
        return None
    cos_t = dot / (mag1 * mag2)
    cos_t = max(-1.0, min(1.0, cos_t))  # clamp
    return math.degrees(math.acos(cos_t))

cap = cv2.VideoCapture(0)
ema_angle = None

with mp_hands.Hands(min_detection_confidence=0.6,
                    min_tracking_confidence=0.6) as hands:
    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        if res.multi_hand_landmarks:
            for hand_landmarks in res.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                # จุด landmark
                thumb_tip = hand_landmarks.landmark[2]
                index_tip = hand_landmarks.landmark[8]
                wrist = hand_landmarks.landmark[0]

                x1, y1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
                x2, y2 = int(index_tip.x * w), int(index_tip.y * h)
                x0, y0 = int(wrist.x * w), int(wrist.y * h)

                v1 = (x1 - x0, y1 - y0)
                v2 = (x2 - x0, y2 - y0)
                angle = calc_angle(v1, v2)

                if angle is not None:
                    # smooth
                    if ema_angle is None:
                        ema_angle = angle
                    else:
                        ema_angle = EMA_ALPHA * angle + (1 - EMA_ALPHA) * ema_angle

                    # map มุม (0–90) → servo (0–180)
                    servo_deg = int(max(0, min(180, round(ema_angle * 2))))

                    # ส่งไป Arduino
                    ser.write(f"{servo_deg}\n".encode())

                    cv2.putText(frame,
                                f"Angle: {int(angle)} | Servo: {servo_deg}",
                                (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 0),
                                2)

                if SHOW_POINTS:
                    cv2.circle(frame, (x1, y1), 6, (255, 0, 0), -1)
                    cv2.circle(frame, (x2, y2), 6, (0, 0, 255), -1)
                    cv2.circle(frame, (x0, y0), 6, (0, 255, 255), -1)

        cv2.imshow("Finger → Servo", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
