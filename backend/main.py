from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from gesture_logic import detect_gesture
from evaluator import evaluate_expr
from digit_predictor import predict_digit
import cv2
import base64
import threading
import time
import numpy as np
import json
import asyncio
import mediapipe as mp

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
clients = []
loop = asyncio.get_event_loop()
drawing = False
expr = ""
result = ""
draw_points = []
camera_active = False

# Mediapipe init once
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

@app.get("/")
def root():
    return {"message": "AirMath backend aktif"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global camera_active
    await websocket.accept()
    clients.append(websocket)
    print("✅ Client connected")

    try:
        while True:
            msg = await websocket.receive_text()

            if msg == "start":
                camera_active = True
                print("📷 Kamera ON")
            elif msg == "stop":
                camera_active = False
                print("📴 Kamera OFF")
    except:
        print("⚠️ Client disconnected")
        if websocket in clients:
            clients.remove(websocket)
        if not clients:
            camera_active = False
        await websocket.close()

def convert_points_to_image(points, size=(28, 28)):
    canvas = np.zeros((480, 640), dtype=np.uint8)
    for i in range(1, len(points)):
        cv2.line(canvas, points[i - 1], points[i], 255, 12)

    if points:
        x_vals = [p[0] for p in points]
        y_vals = [p[1] for p in points]
        min_x, max_x = max(min(x_vals) - 10, 0), min(max(x_vals) + 10, 640)
        min_y, max_y = max(min(y_vals) - 10, 0), min(max(y_vals) + 10, 480)
        canvas = canvas[min_y:max_y, min_x:max_x]

    img = cv2.resize(canvas, size)
    img = 255 - img
    img = img.astype("float32") / 255.0
    return img

def camera_loop():
    global drawing, expr, result, draw_points, camera_active

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Kamera tidak tersedia.")
        return

    while True:
        if not camera_active:
            time.sleep(0.1)
            continue

        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 480))
        gesture, index_pos, frame = detect_gesture(frame)
        
        # Reset drawing setiap frame
        drawing = False

        if gesture == "draw":
            drawing = True
        elif gesture == "clear":
            draw_points.clear()
            expr = ""
            result = ""
        elif gesture == "fist":
            if draw_points:
                img = convert_points_to_image(draw_points)
                digit = predict_digit(img)
                expr += str(digit)
                draw_points.clear()
            elif expr:
                result = evaluate_expr(expr)
        # "pause" dan lainnya tidak mengubah apa-apa

        if drawing and index_pos:
            draw_points.append(index_pos)

        if len(expr) > 20:
            expr = expr[-20:]

        for i in range(1, len(draw_points)):
            cv2.line(frame, draw_points[i - 1], draw_points[i], (0, 255, 0), 4)

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

# Run camera loop
threading.Thread(target=camera_loop, daemon=True).start()