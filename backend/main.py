from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from gesture_logic import detect_gesture
from evaluator import evaluate_expr
import cv2
import base64
import threading
import time
import numpy as np
import json
import asyncio

app = FastAPI()

# CORS biar frontend bisa akses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []
loop = asyncio.get_event_loop()

@app.get("/")
def root():
    return {"message": "AirMath backend aktif"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    print("✅ Client connected")

    try:
        while True:
            await websocket.receive_text()
    except:
        print("⚠️ Client disconnected")
        clients.remove(websocket)
        await websocket.close()

# ====== VAR GLOBAL SHARED STATE ======
drawing = False
expr = ""
result = ""
draw_points = []

# ====== CAMERA LOOP UTAMA ======
def camera_loop():
    global drawing, expr, result, draw_points
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Kamera tidak tersedia.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 480))
        gesture, frame = detect_gesture(frame)

        if gesture == "draw":
            drawing = True
        elif gesture == "pause":
            drawing = False
        elif gesture == "clear":
            draw_points.clear()
            expr = ""
            result = ""
        elif gesture == "fist" and expr:
            result = evaluate_expr(expr)

        # Ambil titik telunjuk (index finger)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        import mediapipe as mp
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0].landmark
            index = lm[8]
            h, w = frame.shape[:2]
            cx, cy = int(index.x * w), int(index.y * h)

            if drawing:
                draw_points.append((cx, cy))

        # Gambar coretan
        for i in range(1, len(draw_points)):
            cv2.line(frame, draw_points[i - 1], draw_points[i], (0, 255, 0), 4)

        # Encode & kirim via WebSocket
        _, jpeg = cv2.imencode('.jpg', frame)
        b64 = base64.b64encode(jpeg.tobytes()).decode('utf-8')

        for ws in clients.copy():
            try:
                data = {
                    "image": b64,
                    "expression": expr,
                    "result": result
                }
                asyncio.run_coroutine_threadsafe(ws.send_text(json.dumps(data)), loop)
            except:
                pass

        time.sleep(1 / 30)

# Mulai thread kamera
threading.Thread(target=camera_loop, daemon=True).start()
