import React, { useEffect, useState } from 'react'

export default function Countdown({ seconds = 3, onFinish }) {
  const [count, setCount] = useState(seconds)

  useEffect(() => {
    setCount(seconds)
    // Start countdown immediately
    if (count === 0) return
    const id = setTimeout(() => {
      setCount(count - 1)
      if (count - 1 === 0 && onFinish) {
        onFinish()
      }
    }, 1000)
    return () => clearTimeout(id)
  }, [count, onFinish])

  return (
    <div className="countdown">
      <div className="countdown-number">{count}</div>
      <div className="countdown-text">Get ready...</div>
    </div>
  )
}

