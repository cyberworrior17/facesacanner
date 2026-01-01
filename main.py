# ==================================================
# coded by mr.virus hacker @ukonwn_virus404x ig account
# Ethical | Offline | CCTV Compatible
# ==================================================

import cv2
import os
import csv
import time
import logging
import configparser
from datetime import datetime
from deepface import DeepFace

# ---------- DIRECTORIES ----------
os.makedirs("logs", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)

# ---------- LOGGING ----------
logging.basicConfig(
    filename="logs/system.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

# ---------- LOAD CONFIG ----------
cfg = configparser.ConfigParser()
cfg.read("config.ini")

mode = cfg["CAMERA"]["mode"]
device = int(cfg["CAMERA"]["device"])
rtsp_url = cfg["CAMERA"]["rtsp_url"]
width = int(cfg["CAMERA"]["width"])
height = int(cfg["CAMERA"]["height"])

auto_blur = cfg.getboolean("PRIVACY", "auto_blur")
auto_save = cfg.getboolean("REPORT", "auto_save")
interval = int(cfg["REPORT"]["interval_minutes"]) * 60

crowd_limit = int(cfg["ALERTS"]["crowd_limit"])
emotion_alert = cfg["ALERTS"]["emotion_alert"]
max_fps = int(cfg["PERFORMANCE"]["max_fps"])

# ---------- CAMERA ----------
cap = cv2.VideoCapture(device if mode == "usb" else rtsp_url)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# ---------- SESSION ----------
session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_file = f"reports/stranger_{session_id}.csv"
last_save = time.time()
rows = []

logging.info("SYSTEM STARTED")

def blur_face(frame, region):
    x, y, w, h = region["x"], region["y"], region["w"], region["h"]
    face = frame[y:y+h, x:x+w]
    frame[y:y+h, x:x+w] = cv2.GaussianBlur(face, (99, 99), 30)

# ---------- MAIN LOOP ----------
while True:
    start = time.time()
    ret, frame = cap.read()
    if not ret:
        logging.error("Camera connection failed")
        break

    strangers = 0

    try:
        results = DeepFace.analyze(
            frame,
            actions=["age", "gender", "emotion"],
            enforce_detection=False
        )
        if not isinstance(results, list):
            results = [results]

        for r in results:
            region = r.get("region")
            if region:
                strangers += 1
                if auto_blur:
                    blur_face(frame, region)

                rows.append([
                    datetime.now().strftime("%H:%M:%S"),
                    r.get("age", "N/A"),
                    r.get("dominant_gender", "N/A"),
                    r.get("dominant_emotion", "N/A")
                ])

                if r.get("dominant_emotion") == emotion_alert:
                    logging.warning("Emotion alert triggered")

    except Exception:
        pass

    if strangers >= crowd_limit:
        logging.warning(f"CROWD ALERT: {strangers} strangers")

    # ---------- HUD ----------
    cv2.putText(frame, f"STRANGERS: {strangers}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.putText(frame, "MR.VIRUS | PRODUCTION", (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # ---------- RED CREDIT TEXT ----------
    cv2.putText(
        frame,
        "CODED BY MR.VIRUS HACKER | ANY PROBLEM IG: @uknown_virus404x",
        (20, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),   # 🔴 RED
        2
    )

    cv2.imshow("MR_VIRUS_STRANGER_SYSTEM", frame)

    # ---------- AUTO SAVE ----------
    if auto_save and time.time() - last_save >= interval:
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "age_est", "gender_est", "emotion_est"])
            writer.writerows(rows)
        last_save = time.time()
        logging.info("Auto report saved")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    delay = max(0, (1 / max_fps) - (time.time() - start))
    time.sleep(delay)

# ---------- CLEANUP ----------
cap.release()
cv2.destroyAllWindows()
logging.info("SYSTEM STOPPED")
