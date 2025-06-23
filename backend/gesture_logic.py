import mediapipe as mp
import cv2

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

def detect_gesture(frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    gesture = "none"

    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]
        lm = handLms.landmark

        thumb = lm[4]
        index = lm[8]
        pinky = lm[20]

        def distance(a, b):
            return ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5

        dist_thumb_index = distance(thumb, index)
        dist_thumb_pinky = distance(thumb, pinky)

        if dist_thumb_index < 0.05:
            gesture = "pause"
        elif dist_thumb_pinky < 0.05:
            gesture = "clear"
        elif thumb.y > index.y:  # fist = semua jari di bawah
            gesture = "fist"
        else:
            gesture = "draw"

        mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

    return gesture, frame
