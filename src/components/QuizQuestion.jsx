import React from 'react'

export default function QuizQuestion({ q, onAnswer, selectedIndex }) {
  return (
    <div className="question-card">
      <div className="question-text">{q.text}</div>
      <div className="options">
        {q.options.map((opt, idx) => (
          <button
            key={idx}
            className={"option " + (selectedIndex === idx ? 'selected' : '')}
            onClick={() => onAnswer(idx)}
            >
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}
