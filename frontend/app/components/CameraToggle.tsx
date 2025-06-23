'use client'

import { useState } from 'react'

export default function CameraToggle({ onToggle }: { onToggle: (state: boolean) => void }) {
  const [active, setActive] = useState(false)

  const toggle = () => {
    const newState = !active
    setActive(newState)
    onToggle(newState)
  }

  return (
    <button
      onClick={toggle}
      className={`px-4 py-2 rounded-xl font-bold ${
        active ? 'bg-red-600' : 'bg-green-500'
      } text-white`}
    >
      {active ? 'Matikan Kamera' : 'Nyalakan Kamera'}
    </button>
  )
}
