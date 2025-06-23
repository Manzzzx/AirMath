'use client'

import { useState } from 'react'
import CameraToggle from './components/CameraToggle'
import VideoCanvas from './components/VideoCanvas'
import ResultBox from './components/ResultBox'

export default function Home() {
  const [cameraOn, setCameraOn] = useState(false)
  const [expr, setExpr] = useState('')
  const [result, setResult] = useState('')

  return (
    <main className="p-6 max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">🧠 AirMath</h1>

      <CameraToggle onToggle={setCameraOn} />

      {cameraOn && (
        <VideoCanvas
          wsUrl="ws://localhost:8000/ws"
          onResult={(e, r) => {
            setExpr(e)
            setResult(r)
          }}
        />
      )}

      <ResultBox expr={expr} result={result} />
    </main>
  )
}
