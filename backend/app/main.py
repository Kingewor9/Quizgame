import os
import json
from fastapi import FastAPI, HTTPException, Request, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from dotenv import load_dotenv
from .db import connect, close, db
from . import crud
from .schemas import QuizCreate, SubmitRequest

load_dotenv()

# Admin API key for protecting quiz creation (set in .env)
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')

app = FastAPI(title="Footy IQ API")

# CORS - allow frontend dev server
FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', 'http://localhost:5173')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event('startup')
async def startup_event():
    await connect()

@app.on_event('shutdown')
async def shutdown_event():
    await close()


@app.get('/admin', response_class=HTMLResponse)
async def admin_page():
    html = """
        <!doctype html>
        <html>
            <head>
                <meta charset="utf-8">
                <title>Admin - Create Quiz</title>
                <style>
                    body{font-family:Arial,Helvetica,sans-serif;padding:20px;background:#0b0b0b;color:#f4f4f4}
                    input,textarea,select{width:100%;padding:8px;border-radius:6px;border:1px solid #333;background:#0f0f0f;color:#fff}
                    label{display:block;margin:8px 0}
                    .box{max-width:900px;margin:0 auto}
                    button{padding:10px 14px;border-radius:6px;background:#fff;color:#000;border:0;cursor:pointer}
                    .question {border:1px solid #222;padding:10px;border-radius:6px;margin-bottom:8px}
                    .options-row{display:flex;gap:8px}
                    .options-row input{flex:1}
                </style>
                <script>
                    function addQuestion() {
                        const container = document.getElementById('questions')
                        const idx = container.children.length + 1
                        const q = document.createElement('div')
                        q.className = 'question'
                        q.innerHTML = `
                            <label>Question ID: <input name="qid" value="q${idx}" /></label>
                            <label>Text: <input name="qtext" value="" /></label>
                            <div class="options-row">
                              <input name="opt" placeholder="Option 1" />
                              <input name="opt" placeholder="Option 2" />
                              <input name="opt" placeholder="Option 3" />
                              <input name="opt" placeholder="Option 4" />
                            </div>
                            <label>Correct option index (0-based): <input name="answerIndex" value="0" /></label>
                        `
                        container.appendChild(q)
                    }
                    function prepareAndSubmit(ev) {
                        ev.preventDefault();
                        const form = document.getElementById('quizForm')
                        const qs = []
                        const container = document.getElementById('questions')
                        for (const q of container.children) {
                            const id = q.querySelector('input[name=qid]').value.trim()
                            const text = q.querySelector('input[name=qtext]').value.trim()
                            const opts = Array.from(q.querySelectorAll('input[name=opt]')).map(i => i.value).filter(Boolean)
                            const answerIndexRaw = q.querySelector('input[name=answerIndex]').value
                            const answerIndex = answerIndexRaw === '' ? null : Number(answerIndexRaw)
                            qs.push({ id, text, options: opts, answerIndex })
                        }
                        document.getElementById('questions_json').value = JSON.stringify(qs)
                        form.submit()
                    }
                    window.addEventListener('DOMContentLoaded', () => addQuestion())
                </script>
            </head>
            <body>
                <div class="box">
                    <h2>Create Quiz</h2>
                    <form id="quizForm" method="post" action="/admin/create" onsubmit="prepareAndSubmit(event)">
                        <label>Admin Key: <input name="key" type="password" required /></label>
                        <label>Title: <input name="title" required /></label>
                        <label>Duration (seconds): <input name="durationSeconds" value="90" /></label>
                        <label>Start ISO date: <input name="startDate" placeholder="2025-11-20T00:00:00Z" /></label>
                        <label>End ISO date: <input name="endDate" placeholder="2025-11-27T00:00:00Z" /></label>
                        <div id="questions"></div>
                        <input type="hidden" id="questions_json" name="questions" />
                        <div style="display:flex;gap:8px;margin-top:8px">
                          <button type="button" onclick="addQuestion()">Add Question</button>
                          <button type="submit">Create Quiz</button>
                        </div>
                    </form>
                </div>
            </body>
        </html>
        """
    return HTMLResponse(content=html)


@app.post('/admin/create', response_class=HTMLResponse)
async def admin_create(
        key: str = Form(...),
        title: str = Form(...),
        durationSeconds: int = Form(90),
        startDate: str = Form(None),
        endDate: str = Form(None),
        questions: str = Form(...)
):
        # validate key
        if ADMIN_API_KEY and key != ADMIN_API_KEY:
                return HTMLResponse(content="<h3>Invalid admin key</h3>", status_code=401)
        try:
            qlist = json.loads(questions)
        except Exception as e:
            return HTMLResponse(content=f"<h3>Invalid questions JSON: {e}</h3>", status_code=400)

        # Validate questions: must have id, text, options (>=2) and answerIndex
        for idx, q in enumerate(qlist, start=1):
            if not isinstance(q.get('id'), str) or not q.get('id'):
                return HTMLResponse(content=f"<h3>Question {idx} missing id</h3>", status_code=400)
            if not isinstance(q.get('text'), str) or not q.get('text'):
                return HTMLResponse(content=f"<h3>Question {idx} missing text</h3>", status_code=400)
            opts = q.get('options')
            if not isinstance(opts, list) or len(opts) < 2:
                return HTMLResponse(content=f"<h3>Question {idx} must have at least 2 options</h3>", status_code=400)
            # coerce answerIndex to int when possible
            ai = q.get('answerIndex')
            try:
                ai_int = int(ai)
            except Exception:
                return HTMLResponse(content=f"<h3>Question {idx} has invalid answerIndex</h3>", status_code=400)
            if ai_int < 0 or ai_int >= len(opts):
                return HTMLResponse(content=f"<h3>Question {idx} answerIndex out of range</h3>", status_code=400)
            # store normalized integer answerIndex back
            q['answerIndex'] = ai_int

        payload = {
            'title': title,
            'questions': qlist,
            'durationSeconds': durationSeconds,
            'startDate': startDate,
            'endDate': endDate
        }
        created = await crud.create_quiz(payload)
        frontend_base = os.getenv('FRONTEND_BASE', 'http://localhost:5173')
        link = f"{frontend_base}/quiz/{created['id']}"
        return HTMLResponse(content=f"<h3>Quiz created</h3><p>ID: {created['id']}</p><p>Link: <a href=\"{link}\">{link}</a></p>")

@app.get('/api/quizzes/{quiz_id}')
async def get_quiz_endpoint(quiz_id: str):
    data = await crud.get_quiz_public(quiz_id)
    if not data:
        raise HTTPException(status_code=404, detail='Quiz not found')
    return data

@app.post('/api/quizzes/{quiz_id}/submit')
async def submit_quiz_endpoint(quiz_id: str, req: SubmitRequest):
    try:
        result = await crud.submit_quiz(quiz_id, req.username, [a.dict() for a in req.answers])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # compute global position
    leaderboard = await crud.get_leaderboard(200)
    position = next((i+1 for i,u in enumerate(leaderboard) if u['username'] == req.username), None)
    response = {
        'username': req.username,
        'points': result['points'],
        'correctCount': result['correctCount'],
        'totalQuestions': result['totalQuestions'],
        'position': position
    }
    return response

@app.get('/api/leaderboard')
async def leaderboard_endpoint(limit: int = 100):
    lb = await crud.get_leaderboard(limit)
    return lb

@app.get('/api/quizzes/{quiz_id}/players')
async def quiz_players_endpoint(quiz_id: str):
    players = await crud.get_quiz_players(quiz_id)
    return players

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})
