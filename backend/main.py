from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
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


def camera_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Kamera tidak tersedia.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 480))
        _, jpeg = cv2.imencode('.jpg', frame)
        b64 = base64.b64encode(jpeg.tobytes()).decode('utf-8')

        # Buat data JSON
        data = json.dumps({
            "image": b64,
            "expression": "2+3",
            "result": "5"
        })

        # Kirim ke semua client pakai thread-safe method
        for ws in clients.copy():
            try:
                asyncio.run_coroutine_threadsafe(ws.send_text(data), loop)
            except:
                pass

        time.sleep(1/30)


# Start kamera di thread terpisah
threading.Thread(target=camera_loop, daemon=True).start()
