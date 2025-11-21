# Footy IQ Backend (FastAPI + MongoDB)

This is a minimal backend for the Footy IQ frontend. It uses FastAPI and MongoDB (Motor) to:

- Create quizzes and return a unique link
- Serve public quiz data (without answers)
- Accept quiz submissions (enforcing one-play-per-username per quiz)
- Maintain a simple leaderboard (total scores aggregated per username)
- List players who played a particular quiz

Requirements
- Python 3.10+
- MongoDB (local or remote)

Quick start
1. Copy `.env.example` to `.env` and set `MONGO_URI` and `FRONTEND_BASE` as needed.

2. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate     # Windows PowerShell
pip install -r requirements.txt
```

3. Run the server:

```bash
uvicorn app.main:app --reload --port 8000
```

API
- POST `/api/quizzes` - create a quiz. Body: QuizCreate (see `app/schemas.py`). Returns `{id, link}`.
 - POST `/api/quizzes` - create a quiz. Body: QuizCreate (see `app/schemas.py`). Returns `{id, link}`. This endpoint is protected by an admin API key passed in the `x-api-key` header when `ADMIN_API_KEY` is set in the server `.env`.
- GET `/api/quizzes/{quiz_id}` - fetch public quiz data (questions do not include correct answers).
- POST `/api/quizzes/{quiz_id}/submit` - submit a quiz. Body: `{username, answers: [{questionId, selectedIndex}]}`. Returns score and position.
- GET `/api/leaderboard` - get global leaderboard sorted by totalScore.
- GET `/api/quizzes/{quiz_id}/players` - players who played that quiz.

Notes
- The backend enforces a unique play per (quiz_id, username) and will return a 400 if a user tries to play the same quiz again.
- Leaderboard stores accumulated `totalScore` per username.

Admin script: create_quiz
---------------------------------
We included a small admin CLI script at `backend/scripts/create_quiz.py` which can:

- Read a JSON quiz file (see `backend/samples/sample_quiz.json`) and POST it to the API.
- Or run interactively to build a quiz in the terminal.

Usage (after activating your Python env and starting the server):

```bash
python backend/scripts/create_quiz.py --file backend/samples/sample_quiz.json
```

Or interactively:

```bash
python backend/scripts/create_quiz.py
```

The script will print the returned link e.g. `http://localhost:5173/quiz/<id>` which you can share.

Admin web form
--------------
The server also exposes a minimal admin web form at `GET /admin` where you can paste quiz JSON and provide the admin key. The form POSTs to `/admin/create` and returns the created quiz link. Set `ADMIN_API_KEY` in your `.env` to protect both the API endpoint and the admin form.

Next steps / improvements
- Add authentication for quiz creation and admin endpoints.
- Add validation and sanitization of incoming quiz data.
- Add pagination and filters for leaderboard and players.
- Add an admin UI or CLI tool to create quizzes conveniently (or POST from a simple form).
