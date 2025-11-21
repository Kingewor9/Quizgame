export const SAMPLE_QUIZ = {
  id: 'sample-quiz',
  title: "Footy IQ - Today's Quiz",
  questions: [
    {
      id: 'q1',
      text: 'Which country won the 2018 FIFA World Cup?',
      options: ['France', 'Croatia', 'Brazil', 'Germany'],
      answerIndex: 0
    },
    {
      id: 'q2',
      text: 'Who has won the most Ballon d\'Or awards (as of 2021)?',
      options: ['Cristiano Ronaldo', 'Lionel Messi', 'Zinedine Zidane', 'Pele'],
      answerIndex: 1
    },
    {
      id: 'q3',
      text: 'Which club is known as The Red Devils?',
      options: ['Liverpool', 'Manchester United', 'Arsenal', 'Chelsea'],
      answerIndex: 1
    }
  ],
  // 90 seconds allowed
  durationSeconds: 90,
  // start and end dates for demo — set to allow play now
  startDate: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
  endDate: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString()
}
