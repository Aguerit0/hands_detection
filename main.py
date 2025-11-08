import cv2
import os
import mediapipe as mp
import numpy as np

#configs
FOLDER_PATH = "img"
WIDTH, HEIGHT = 1280, 720
SCREEN_W, SCREEN_H = 1600, 900
CAM_RATIO = 0.25
MARGIN = 40
GESTURE_THRESHOLD = 300
BTN_DELAY = 10

#mediapipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)


def init_camera():
    cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    if not cap.isOpened():
        raise RuntimeError("Error al abrir la cámara.")
    print("Cámara abierta.")
    return cap

def get_images(folder_path):
    imgs = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return sorted(imgs, key=len)

def detect_hands(img):
    img_rgb = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
    results = hands_detector.process(img_rgb)
    hands = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = img.shape
                lm_list.append((int(lm.x * w), int(lm.y * h)))
            hands.append(lm_list)
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    return hands, cv2.flip(img, 1)

def fingers_up(lm_list):
    #DEVUELVOD ARRAY CON DEDOS LEVANTADOS [PULGAR, ÍNDICE, MEDIO, ANULAR, MEÑIQUE]
    if not lm_list or len(lm_list) < 21:
        return [0, 0, 0, 0, 0]
    fingers = []
    # Pulgar
    fingers.append(1 if lm_list[4][0] > lm_list[3][0] else 0)
    # Dedos restantes
    for tip in [8, 12, 16, 20]:
        fingers.append(1 if lm_list[tip][1] < lm_list[tip - 2][1] else 0)
    return fingers

def process_gestures(hands, img_num, total_imgs):
    button_pressed = False
    for lm_list in hands:
        cx, cy = lm_list[9]  #centro aproximado (punto medio de la palma)
        fingers = fingers_up(lm_list)
        if cy <= GESTURE_THRESHOLD:
            #pulgar levantado -> anterior
            if fingers == [1, 0, 0, 0, 0] and img_num > 0:
                img_num -= 1
                button_pressed = True
                print("<- Slide anterior")

            # meñique levantado -> siguiente
            elif fingers == [0, 0, 0, 0, 1] and img_num < total_imgs - 1:
                img_num += 1
                button_pressed = True
                print("-> Slide siguiente")
    return img_num, button_pressed

def show_slides(curr_img, img, screen_w, screen_h, cam_ratio, margin):
    curr_img = cv2.resize(curr_img, (screen_w, screen_h))
    cam_w = int(screen_w * cam_ratio)
    cam_h = int(cam_w * (9 / 16))
    img_small = cv2.resize(img, (cam_w, cam_h))
    y1 = screen_h - cam_h - margin
    y2 = y1 + cam_h
    x1 = screen_w - cam_w - margin
    x2 = x1 + cam_w
    curr_img[y1:y2, x1:x2] = img_small
    return curr_img

#MAIN
if __name__ == "__main__":
    cap = init_camera()
    path_imgs = get_images(FOLDER_PATH)
    img_num = 0
    button_pressed = False
    count_btn = 0

    #lienzo de dibujos
    canvas = np.zeros((SCREEN_H, SCREEN_W, 3), np.uint8)
    draw_mode = False
    prev_x, prev_y = 0, 0

    cv2.namedWindow("Presentación", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Presentación", SCREEN_W, SCREEN_H)

    while True:
        success, img = cap.read()
        if not success:
            print("Error al abrir la cámara.")
            break

        hands, img = detect_hands(img)
        cv2.line(img, (0, GESTURE_THRESHOLD), (WIDTH, GESTURE_THRESHOLD), (0, 255, 0), 3)

        if hands and not button_pressed:
            img_num, button_pressed = process_gestures(hands, img_num, len(path_imgs))

        if button_pressed:
            count_btn += 1
            if count_btn > BTN_DELAY:
                button_pressed = False
                count_btn = 0

        path_full_img = os.path.join(FOLDER_PATH, path_imgs[img_num])
        curr_img = cv2.imread(path_full_img)
        if curr_img is None:
            print(f"Error al cargar la imagen: {path_full_img}")
            break

        curr_img = cv2.resize(curr_img, (SCREEN_W, SCREEN_H))

        #dibujo y puntero
        if hands:
            lm_list = hands[0]
            fingers = fingers_up(lm_list)
            x, y = lm_list[8]  #punta del índice

            #solo índice levantado -> dibujo
            if fingers == [0, 1, 0, 0, 0]:
                draw_mode = True
                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = x, y
                cv2.line(canvas, (prev_x, prev_y), (x, y), (0, 0, 255), 10)
                prev_x, prev_y = x, y

            #índice y medio levantados -> puntero
            elif fingers == [0, 1, 1, 0, 0]:
                draw_mode = False
                prev_x, prev_y = 0, 0
                cv2.circle(curr_img, (x, y), 12, (0, 0, 255), cv2.FILLED)

            else:
                draw_mode = False
                prev_x, prev_y = 0, 0

        #camara + slide + dibujo
        img_combined = show_slides(curr_img, img, SCREEN_W, SCREEN_H, CAM_RATIO, MARGIN)
        mask = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, inv_mask = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)
        inv_mask = cv2.bitwise_not(inv_mask)
        img_combined = cv2.bitwise_and(img_combined, img_combined, mask=inv_mask)
        img_combined = cv2.add(img_combined, canvas)

        cv2.imshow("Presentación", img_combined)
        cv2.imshow("Cámara", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('n'):
            img_num = (img_num + 1) % len(path_imgs)
        elif key == ord('c'):
            canvas = np.zeros((SCREEN_H, SCREEN_W, 3), np.uint8)
            print("Lienzo limpiado.")

    cap.release()
    cv2.destroyAllWindows()
