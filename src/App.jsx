import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import QuizPage from './pages/QuizPage'
import LeaderboardPage from './pages/LeaderboardPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/quiz/sample-quiz" replace />} />
      <Route path="/quiz/:quizId" element={<QuizPage />} />
      <Route path="/leaderboard" element={<LeaderboardPage />} />
    </Routes>
  )
}
