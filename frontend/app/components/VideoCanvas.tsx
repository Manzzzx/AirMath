"use client";

import { useEffect, useRef, useState } from "react";

export default function VideoCanvas({ wsUrl, onResult }: { wsUrl: string; onResult: (expr: string, result: string) => void }) {
  const [imageSrc, setImageSrc] = useState("");
  const [connected, setConnected] = useState(false);
  const [cameraOn, setCameraOn] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      setConnected(true);
      if (cameraOn) socket.send("start");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.image) setImageSrc(`data:image/jpeg;base64,${data.image}`);
      if (data.expression || data.result) {
        onResult(data.expression, data.result);
      }
    };

    socket.onclose = () => {
      setConnected(false);
    };

    return () => {
      if (socket.readyState === 1) {
        socket.send("stop");
      }
      socket.close();
    };
  }, [wsUrl, onResult]);

  const toggleCamera = () => {
    if (!socketRef.current || socketRef.current.readyState !== 1) return;

    const action = cameraOn ? "stop" : "start";
    socketRef.current.send(action);
    setCameraOn(!cameraOn);
  };

  return (
    <div className="relative my-6">
      <div className="rounded-xl overflow-hidden aspect-video bg-black border border-white/10 shadow-lg">
        {imageSrc ? <img src={imageSrc} alt="Live Feed" className="w-full h-full object-cover" /> : <p className="text-center text-white py-8">🔌 Kamera belum aktif</p>}
      </div>

      <div className="absolute top-2 right-2 flex items-center gap-2">
        <span className={`text-xs px-3 py-1 rounded-full ${connected ? "bg-green-600" : "bg-red-500"} text-white`}>{connected ? "Terhubung" : "Terputus"}</span>

        <button onClick={toggleCamera} className="text-sm px-4 py-1 rounded-full bg-white text-black hover:bg-gray-200 transition">
          {cameraOn ? "🔴 Stop" : "🟢 Start"}
        </button>
      </div>
    </div>
  );
}
