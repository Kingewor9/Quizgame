import React, { useEffect, useState, useRef } from 'react'

export default function Timer({ initialSeconds, running, onExpire }) {
  const [seconds, setSeconds] = useState(initialSeconds)
  const onExpireRef = useRef(onExpire)

  useEffect(() => {
    onExpireRef.current = onExpire
  }, [onExpire])

  useEffect(() => {
    setSeconds(initialSeconds)
  }, [initialSeconds])

  useEffect(() => {
    if (!running) return
    const id = setInterval(() => {
      setSeconds(s => {
        if (s <= 1) {
          clearInterval(id)
          if (onExpireRef.current) onExpireRef.current()
          return 0
        }
        return s - 1
      })
    }, 1000)
    return () => clearInterval(id)
  }, [running])

  return <div className="timer">{seconds}s</div>
}
