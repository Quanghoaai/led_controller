import cv2
import mediapipe as mp
import time
import numpy as np
import threading
from ui import SmartHomeApp
import tkinter as tk
from PIL import ImageFont, ImageDraw, Image

# Đường dẫn tới font Unicode tiếng Việt
FONT_PATH = "C:/Windows/Fonts/arial.ttf"  # Thay đổi cho phù hợp nếu dùng font khác

def draw_text_unicode(img_cv, text, position, font_size=40, color=(255, 0, 0)):
    """Vẽ chữ Unicode lên ảnh OpenCV bằng Pillow."""
    img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except Exception as e:
        font = ImageFont.load_default()
        print(f"Lỗi load font: {e}. Sử dụng font mặc định.")
    draw.text(position, text, font=font, fill=color[::-1])
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def control_devices_by_fingers(app, total):
    app.set_device_states(False, False, False, False, False)
    if total == 1:
        app.set_device_states(True, False, False, False, False)
    elif total == 2:
        app.set_device_states(False, True, False, False, False)
    elif total == 3:
        app.set_device_states(False, False, True, False, False)
    elif total == 4:
        app.set_device_states(False, False, False, True, False)
    elif total == 5:
        app.set_device_states(False, False, False, False, True)

def ai_finger_recognition_loop(app):
    time.sleep(2.0)
    mp_draw = mp.solutions.drawing_utils
    mp_hand = mp.solutions.hands
    tipIds = [4, 8, 12, 16, 20]
    video = cv2.VideoCapture(0)

    # Tên cửa sổ có dấu tiếng Việt, sẽ chỉ hiện đúng nếu hệ điều hành và Python hỗ trợ
    window_name = "Hand Detection"

    # Tạo cửa sổ trước (giúp hiển thị Unicode tốt hơn trên nhiều hệ điều hành)
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    with mp_hand.Hands(min_detection_confidence=0.5,
                       min_tracking_confidence=0.5) as hands:
        while True:
            ret, image = video.read()
            if not ret:
                continue
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = hands.process(image_rgb)
            image_rgb.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            lmList = []
            if results.multi_hand_landmarks:
                myHands = results.multi_hand_landmarks[0]
                for id, lm in enumerate(myHands.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                mp_draw.draw_landmarks(image, myHands, mp_hand.HAND_CONNECTIONS)
            fingers = []
            if len(lmList) != 0:
                # Xử lý ngón cái
                if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                for id in range(1, 5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                total = fingers.count(1)
                control_devices_by_fingers(app, total)
                cv2.rectangle(image, (20, 300), (320, 425), (0, 255, 0), cv2.FILLED)
                image = draw_text_unicode(image, f"{total} ngón", (45, 340), font_size=60, color=(255, 0, 0))
            # Vẽ tiêu đề vào ảnh bằng font đẹp
            cv2.rectangle(image, (20, 15), (430, 65), (0, 255, 0), cv2.FILLED)
            image = draw_text_unicode(image, "Nhận diện bàn tay", (30, 20), font_size=34, color=(255, 0, 0))
            cv2.imshow(window_name, image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeApp(root)
    threading.Thread(target=ai_finger_recognition_loop, args=(app,), daemon=True).start()
    root.mainloop()