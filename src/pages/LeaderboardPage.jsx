import React, { useEffect, useState } from 'react'
import { ArrowUp, ArrowDown, ArrowRight, Trophy, Users } from 'lucide-react'
import { Link } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function LeaderboardPage() {
  const [lb, setLb] = useState([])

  useEffect(() => {
      let mounted = true
      async function load() {
        try {
          const res = await fetch(`${API_BASE}/api/leaderboard`)
          if (!res.ok) throw new Error('Failed')
          const data = await res.json()
          if (mounted) setLb(data)
        } catch (e) {
          console.error('load leaderboard', e)
          // fallback to localStorage if available
          const raw = localStorage.getItem('leaderboard')
          if (mounted) setLb(raw ? JSON.parse(raw) : [])
        }
      }
      load()
      return () => { mounted = false }
  }, [])

  function formatDelta(i) {
    // For demo we won't track historic positions; show placeholder arrows
    if (i === 0) return <ArrowUp size={16} color="green" />
    if (i === 1) return <ArrowDown size={16} color="orange" />
    return <ArrowRight size={16} />
  }

  return (
    <div className="page-container">
      <header className="header flex items-center justify-between">
        <div className="brand flex items-center gap-2"><Trophy size={20} />Footy IQ</div>
          <div className="nav-quick"><Link to="/">Back to quiz</Link></div>
      </header>

      <main className="main">
        <div className="panel w-full max-w-2xl">
          <h2 className="flex items-center gap-2"><Users size={18} />Global Leaderboard</h2>
          <p className="text-sm text-gray-400">Top players by total score</p>
        </div>

        <div className="leaderboard w-full max-w-2xl">
          {lb.length === 0 && <div className="empty">No entries yet</div>}
          <div className="leader-table">
            <div className="header-row">
              <div className="col rank">Rank</div>
              <div className="col player">Player</div>
              <div className="col points">Points</div>
              <div className="col change">Change</div>
            </div>
            {lb.map((p, idx) => (
              <div key={p.username} className="leader-row">
                <div className="col rank">{idx + 1}</div>
                <div className="col player">{p.username}</div>
                <div className="col points">{p.totalScore}</div>
                <div className="col change">{formatDelta(idx)}</div>
              </div>
            ))}
          </div>
        </div>
      </main>

      <footer className="footer">Footy IQ ©</footer>
    </div>
  )
}
