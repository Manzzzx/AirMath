"use client";

import { useState } from "react";
import VideoCanvas from "./components/VideoCanvas";

export default function HomePage() {
  const [expression, setExpression] = useState("");
  const [result, setResult] = useState("");

  return (
    <main className="max-w-3xl mx-auto px-4 py-8 text-white font-mono">
      <h1 className="text-3xl font-bold mb-6 text-center">✋ AirMath</h1>

      <VideoCanvas
        wsUrl="ws://localhost:8000/ws"
        onResult={(expr, res) => {
          setExpression(expr);
          setResult(res);
        }}
      />

      <div className="bg-gray-900 rounded-xl p-4 mt-6 border border-gray-700 shadow-inner">
        <p className="text-lg">
          ✍️ Ekspresi: <span className="font-bold text-green-400">{expression || "..."}</span>
        </p>
        <p className="text-lg mt-2">
          ✅ Hasil: <span className="font-bold text-yellow-400">{result || "..."}</span>
        </p>
      </div>
    </main>
  );
}
