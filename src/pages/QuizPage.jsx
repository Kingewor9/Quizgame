import React, { useEffect, useMemo, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Timer from '../components/Timer'
import QuizQuestion from '../components/QuizQuestion'
import { ArrowRight, Trophy, Clock, Calendar, Users } from 'lucide-react'

function formatCountdownTo(dateStr) {
  const diff = Math.max(0, new Date(dateStr) - Date.now())
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24)
  const mins = Math.floor((diff / (1000 * 60)) % 60)
  const secs = Math.floor((diff / 1000) % 60)
  return `${days}d ${hours}h ${mins}m ${secs}s`
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function QuizPage() {
  const { quizId } = useParams()
  const navigate = useNavigate()

  const [quiz, setQuiz] = useState(null)
  const [loading, setLoading] = useState(true)

  const [username, setUsername] = useState('')
  const [started, setStarted] = useState(false)
  const [quizRunning, setQuizRunning] = useState(false)
  const [index, setIndex] = useState(0)
  const [selected, setSelected] = useState(null)
  const [answers, setAnswers] = useState({})
  const [showResult, setShowResult] = useState(false)
  const [timeLeft, setTimeLeft] = useState(90)
  const [serverResult, setServerResult] = useState(null)

  // expiration check
  const [expired, setExpired] = useState(false)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      try {
        const res = await fetch(`${API_BASE}/api/quizzes/${quizId}`)
        if (!res.ok) throw new Error('Quiz not found')
        const data = await res.json()
        if (mounted) setQuiz(data)
      } catch (err) {
        console.error(err)
        if (mounted) setQuiz(null)
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [quizId])

  useEffect(() => {
    if (!quiz) return
    const now = new Date()
    setExpired(now < new Date(quiz.startDate) || now > new Date(quiz.endDate))
    setTimeLeft(quiz.durationSeconds || 90)
  }, [quiz])

  async function hasPlayedRemote(username) {
    if (!username || !quiz) return false
    try {
      const res = await fetch(`${API_BASE}/api/quizzes/${quiz.id}/players`)
      if (!res.ok) return false
      const list = await res.json()
      return list.some(p => p.username === username)
    } catch (e) {
      console.error('hasPlayedRemote', e)
      return false
    }
  }

  async function startPressed() {
    if (!username) return alert('Please enter your Telegram username')
    if (!quiz) return alert('Quiz not loaded')
    const played = await hasPlayedRemote(username)
    if (played) return alert('This username has already played this quiz.')
    setStarted(true)
    setQuizRunning(true)
  }

  function handleAnswer(idx) {
    setSelected(idx)
    const newAnswers = { ...answers, [index]: idx }  // capture immediately
    setAnswers(newAnswers)
    // move to next after small delay
    setTimeout(() => {
      setSelected(null)
      if (index + 1 < (quiz?.questions || []).length) {
        setIndex(i => i + 1)
      } else {
        // finished - use captured newAnswers instead of stale state
        endQuizWithAnswers(newAnswers)
      }
    }, 400)
  }

  async function endQuiz(reason) {
    // prepare answers array - include ALL answered questions
    const allAnswers = (quiz.questions || []).map((q, i) => {
      const ans = answers[i]
      console.log(`Question ${i} (${q.id}): answer index = ${ans}`)
      return { questionId: q.id, selectedIndex: ans }
    })
    const payloadAnswers = allAnswers.filter(a => typeof a.selectedIndex === 'number')
    console.log('All answers object:', answers)
    console.log('All mapped answers:', allAnswers)
    console.log('Filtered payload to submit:', payloadAnswers)
    await submitQuizAnswers(payloadAnswers)
  }

  async function endQuizWithAnswers(answersObj) {
    // prepare answers array using the passed-in answers object (captures the last answer)
    const allAnswers = (quiz.questions || []).map((q, i) => {
      const ans = answersObj[i]
      console.log(`Question ${i} (${q.id}): answer index = ${ans}`)
      return { questionId: q.id, selectedIndex: ans }
    })
    const payloadAnswers = allAnswers.filter(a => typeof a.selectedIndex === 'number')
    console.log('All answers object:', answersObj)
    console.log('All mapped answers:', allAnswers)
    console.log('Filtered payload to submit:', payloadAnswers)
    await submitQuizAnswers(payloadAnswers)
  }

  async function submitQuizAnswers(payloadAnswers) {
    setQuizRunning(false)
    try {
      const res = await fetch(`${API_BASE}/api/quizzes/${quiz.id}/submit`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, answers: payloadAnswers })
      })
      const data = await res.json()
      if (!res.ok) {
        alert(data.detail || 'Error submitting quiz')
        setShowResult(false)
        return
      }
      // show server result
      setServerResult(data)
      setShowResult(true)
      // store last result locally for quick access
      localStorage.setItem(`lastResult:${quiz.id}:${username}`, JSON.stringify({ points: data.points, correctCount: data.correctCount, totalQuestions: data.totalQuestions }))
    } catch (e) {
      console.error(e)
      alert('Failed to submit quiz')
    }
  }

  async function onTimerExpire() {
    setQuizRunning(false)
    await endQuiz('timeout')
  }

  useEffect(() => {
    // load any saved last result
    if (!quiz || !username) return
    const res = localStorage.getItem(`lastResult:${quiz.id}:${username}`)
    if (res) setServerResult(JSON.parse(res))
  }, [quiz, username])

  const [expireCountdown, setExpireCountdown] = useState('')
  useEffect(() => {
    if (!quiz) return
    setExpireCountdown(formatCountdownTo(quiz.endDate))
    const id = setInterval(() => setExpireCountdown(formatCountdownTo(quiz.endDate)), 1000)
    return () => clearInterval(id)
  }, [quiz])

  return (
    <div className="page-container">
      <header className="header">
        <div className="brand"><Trophy size={20} />Footy IQ</div>
        <div className="nav-quick" onClick={() => navigate('/leaderboard')}>Leaderboard <ArrowRight size={16} /></div>
      </header>

      <main className="main">
        <div className="panel">
          {loading ? (
            <div>Loading quiz...</div>
          ) : !quiz ? (
            <div>Quiz not found</div>
          ) : (
            <>
              <h2 className="quiz-title"><Trophy size={18} />Today's Quiz</h2>
              <p className="quiz-name">{quiz.title}</p>
              <div className="quiz-stats-grid">
                <div className="stat-item"><Users size={16} /><div><span>Questions</span><strong>{quiz.questions.length}</strong></div></div>
                <div className="stat-item"><Clock size={16} /><div><span>Time</span><strong>{quiz.durationSeconds}s</strong></div></div>
                <div className="stat-item"><div><span>Total points</span><strong>{quiz.questions.length * 10}</strong></div></div>
                <div className="stat-item"><Calendar size={16} /><div><span>Expires in</span><strong>{expireCountdown}</strong></div></div>
              </div>
            </>
          )}
        </div>

        {!started && (
          <div className="start-box">
            {expired ? (
              <div className="expired">This quiz has expired and cannot be played.</div>
            ) : (
              <>
                <label className="label">Telegram username</label>
                <input className="input" value={username} onChange={e => setUsername(e.target.value.trim())} placeholder="@yourusername or username" />
                <button className="btn primary" onClick={startPressed} disabled={!username}>Begin</button>
              </>
            )}
          </div>
        )}

        {quizRunning && quiz && (
          <div className="quiz-area">
            <div className="quiz-top">
              <Timer initialSeconds={quiz.durationSeconds} running={quizRunning} onExpire={onTimerExpire} />
              <div className="progress">Question {index + 1} / {quiz.questions.length}</div>
            </div>
            <QuizQuestion q={quiz.questions[index]} onAnswer={handleAnswer} selectedIndex={selected} />
          </div>
        )}

        {showResult && serverResult && (
          <div className="result-card">
            <h3>Result</h3>
            <p>Points: <strong>{serverResult.points}</strong></p>
            <p>Correct: <strong>{serverResult.correctCount}</strong> / {serverResult.totalQuestions}</p>
            <p>Your position: <strong>{serverResult.position}</strong></p>
            <div className="result-actions">
              <button className="btn" onClick={() => navigate('/leaderboard')}>View Global Leaderboard</button>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">Footy IQ ©</footer>
    </div>
  )
}
