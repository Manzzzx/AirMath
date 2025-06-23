"use client";

import { useEffect, useRef, useState } from "react";

export default function VideoCanvas({ wsUrl, onResult }: { wsUrl: string; onResult: (expr: string, result: string) => void }) {
  const [imageSrc, setImageSrc] = useState("");
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.image) setImageSrc(`data:image/jpeg;base64,${data.image}`);
      if (data.expression || data.result) {
        onResult(data.expression, data.result);
      }
    };

    return () => {
      socket.close();
    };
  }, [wsUrl]);

  return (
    <div className="my-4 border rounded-xl overflow-hidden bg-black aspect-video">
      {imageSrc ? (
        <div className="my-4 rounded-xl overflow-hidden bg-black aspect-video border border-white/20 shadow-md">
          <img src={imageSrc} alt="Live" className="w-full h-full object-cover" />
        </div>
      ) : (
        <p className="text-center text-white p-4">Menunggu stream kamera...</p>
      )}
    </div>
  );
}
