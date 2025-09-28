import re
import speech_recognition as sr
import sys

# กำหนดชื่อไฟล์บันทึกเสียงพูด
LOG_FILE = "rec.txt"

r = sr.Recognizer()
with sr.Microphone() as mic:
    r.adjust_for_ambient_noise(mic, duration=0.6)
    print("พูดคำสั่ง เช่น 'สวัสดี หมุนมอเตอร์ ไปที่ 90 องศา'")
    print("พูดว่า 'หยุด' หรือ 'ออก' เพื่อปิดโปรแกรม")

    while True:
        try:
            audio = r.listen(mic, timeout=6, phrase_time_limit=10)
            text = r.recognize_google(audio, language="th-TH").strip()
            print("ได้ยิน : ", text)

            # ==== บันทึกลงไฟล์ ====
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(text + "\n")

            # === เช็คคำสั่งหยุด ===
            if text in ["หยุด", "ออก"]:
                print("ปิดการทำงานแล้วค่ะ 👋")
                sys.exit(0)

            # === เช็คคำว่า "สวัสดี" ===
            if text.startswith("สวัสดี"):
                cmd = text.replace("สวัสดี", "", 1).strip()
                m = re.search(r"(\d+)", cmd)
                angle = int(m.group(1)) if m else None
                print("สวัสดี : ", cmd, " | มุม : ", angle)

        except sr.WaitTimeoutError:
            print("ไม่มีเสียงพูดมาได้เลยค่ะ...")
        except sr.UnknownValueError:
            print("ฟังไม่ออกค่ะ...")
