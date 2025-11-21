from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from . import db as db_module

async def create_quiz(payload: dict) -> dict:
    quiz_id = str(uuid4())
    doc = {**payload, 'id': quiz_id, 'created_at': datetime.utcnow()}
    await db_module.db.quizzes.insert_one(doc)
    return doc

async def get_quiz(quiz_id: str) -> Optional[dict]:
    return await db_module.db.quizzes.find_one({'id': quiz_id})

async def get_quiz_public(quiz_id: str) -> Optional[dict]:
    q = await get_quiz(quiz_id)
    if not q:
        return None
    # remove answerIndex from questions
    questions = []
    for item in q.get('questions', []):
        questions.append({
            'id': item['id'],
            'text': item['text'],
            'options': item['options']
        })
    return {
        'id': q['id'],
        'title': q.get('title'),
        'questions': questions,
        'durationSeconds': q.get('durationSeconds', 90),
        'startDate': q.get('startDate'),
        'endDate': q.get('endDate')
    }

async def submit_quiz(quiz_id: str, username: str, answers: List[dict]) -> dict:
    q = await get_quiz(quiz_id)
    if not q:
        raise ValueError('Quiz not found')
    # check played
    existing = await db_module.db.plays.find_one({'quiz_id': quiz_id, 'username': username})
    if existing:
        raise ValueError('User has already played this quiz')
    # calc score
    questions = q.get('questions', [])
    # normalize answerIndex to int when possible to avoid string/number mismatches
    qmap = {}
    for it in questions:
        ai = it.get('answerIndex')
        try:
            ai_norm = int(ai) if ai is not None else None
        except Exception:
            ai_norm = None
        copy = dict(it)
        copy['answerIndex'] = ai_norm
        qmap[copy['id']] = copy
    print(f"DEBUG: Quiz {quiz_id} has {len(qmap)} questions. QIDs: {list(qmap.keys())}")
    print(f"DEBUG: Received {len(answers)} answers: {answers}")
    correctCount = 0
    for a in answers:
        qid = a.get('questionId')
        sel_raw = a.get('selectedIndex')
        if qid in qmap:
            # coerce submitted index to int where possible
            try:
                sel = int(sel_raw)
            except Exception:
                print(f"DEBUG: Could not coerce {sel_raw} to int for question {qid}")
                continue
            correct_index = qmap[qid].get('answerIndex')
            print(f"DEBUG: Q{qid}: submitted={sel}, correct={correct_index}, match={sel == correct_index}")
            if correct_index is not None and sel == correct_index:
                correctCount += 1
        else:
            print(f"DEBUG: Question ID {qid} not found in quiz")
    print(f"DEBUG: Final correctCount={correctCount}")
    points = correctCount * 10
    play_doc = {
        'quiz_id': quiz_id,
        'username': username,
        'points': points,
        'correctCount': correctCount,
        'totalQuestions': len(questions),
        'timestamp': datetime.utcnow()
    }
    await db_module.db.plays.insert_one(play_doc)
    # update leaderboard (upsert)
    await db_module.db.leaderboard.update_one({'username': username}, {'$inc': {'totalScore': points}, '$setOnInsert': {'username': username}}, upsert=True)
    # compute position
    cursor = db_module.db.leaderboard.find().sort('totalScore', -1)
    rank = 0
    position = None
    i = 0
    async for doc in cursor:
        i += 1
        if doc.get('username') == username:
            position = i
            break
    return {**play_doc, 'position': position}

async def get_leaderboard(limit: int = 100) -> List[dict]:
    cursor = db_module.db.leaderboard.find().sort('totalScore', -1).limit(limit)
    out = []
    async for doc in cursor:
        out.append({'username': doc['username'], 'totalScore': doc.get('totalScore', 0)})
    return out

async def get_quiz_players(quiz_id: str, limit: int = 100) -> List[dict]:
    cursor = db_module.db.plays.find({'quiz_id': quiz_id}).sort('timestamp', -1).limit(limit)
    out = []
    async for doc in cursor:
        out.append({'username': doc['username'], 'points': doc['points'], 'correctCount': doc['correctCount'], 'timestamp': doc['timestamp']})
    return out
