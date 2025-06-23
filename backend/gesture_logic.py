import mediapipe as mp
import cv2

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

def detect_gesture(frame):
    frame = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    gesture = "none"
    index_pos = None

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            lm = hand_landmarks.landmark
            hand_label = handedness.classification[0].label
            
            tips_id = [4, 8, 12, 16, 20]
            mcp_id = [2, 5, 9, 13, 17]

            jari_terbuka = 0
            for i in range(5):
                if i == 0:
                    if abs(lm[tips_id[i]].x - lm[mcp_id[i]].x) > 0.05:
                        jari_terbuka += 1
                else:
                    if lm[tips_id[i]].y < lm[mcp_id[i]].y:
                        jari_terbuka += 1

            current_gesture = "none"
            if jari_terbuka == 0:
                current_gesture = "fist"
            elif jari_terbuka == 2:
                current_gesture = "clear"
            elif jari_terbuka == 1 and lm[8].y < lm[6].y:
                current_gesture = "draw"
            elif jari_terbuka == 5:
                current_gesture = "pause"

            if gesture == "none" or current_gesture == "draw":
                gesture = current_gesture
                
                if current_gesture == "draw":
                    h, w = frame.shape[:2]
                    index_pos = (int(lm[8].x * w), int(lm[8].y * h))

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    return gesture, index_pos, frame