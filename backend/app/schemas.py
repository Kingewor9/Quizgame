from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class QuestionIn(BaseModel):
    id: str
    text: str
    options: List[str]
    answerIndex: int

class QuestionOut(BaseModel):
    id: str
    text: str
    options: List[str]

class QuizCreate(BaseModel):
    title: str
    questions: List[QuestionIn]
    durationSeconds: int = 90
    startDate: Optional[datetime]
    endDate: Optional[datetime]

class QuizOut(BaseModel):
    id: str
    title: str
    questions: List[QuestionOut]
    durationSeconds: int
    startDate: Optional[datetime]
    endDate: Optional[datetime]

class SubmitAnswer(BaseModel):
    questionId: str
    selectedIndex: int

class SubmitRequest(BaseModel):
    username: str = Field(..., min_length=1)
    answers: List[SubmitAnswer]

class SubmitResponse(BaseModel):
    username: str
    points: int
    correctCount: int
    totalQuestions: int
    position: Optional[int]

class LeaderboardEntry(BaseModel):
    username: str
    totalScore: int

class PlayEntry(BaseModel):
    quiz_id: str
    username: str
    points: int
    correctCount: int
    totalQuestions: int
    timestamp: datetime
