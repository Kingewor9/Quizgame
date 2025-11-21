# Footy IQ - Quiz Frontend Prototype

This is a minimal React (Vite) frontend prototype for a single-quiz page and a global leaderboard. It demonstrates the UI and basic client-side logic described:

- Unique quiz link (eg `/quiz/sample-quiz`)
- Start screen with Telegram username input
- Quiz starts immediately when the user clicks `Begin` (no pre-countdown)
- 90-second quiz timer (displayed in seconds)
- Quiz questions, scoring (10 points per correct answer)
- Single play per username per quiz (stored in `localStorage` for demo)
- Simple global leaderboard simulated via `localStorage`

This project is frontend-only and uses browser `localStorage` to simulate server behavior. The UI includes optional Tailwind CSS classes — to enable Tailwind styling install the Tailwind packages described below.

## Setup (Windows PowerShell)

```powershell
# 1. Install dependencies
npm install

# 2. (optional) If you want Tailwind CSS styling, install the PostCSS/Tailwind packages listed in package.json
#    then run the dev server.

# 3. Run dev server
npm run dev
```

Open the printed local URL (usually `http://localhost:5173`) and go to `/quiz/sample-quiz`.

## Notes
- Replace sample quiz in `src/data/quizzes.js` with your quiz data and set `startDate`/`endDate`.
- When you later add a backend, replace `localStorage` usage with API calls to your server.

