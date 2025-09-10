from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, Enum):
    RADIO = "radio"
    CHECKBOX = "checkbox"


class ReferenceLink(BaseModel):
    title: str
    url: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class VideoResource(BaseModel):
    title: str
    url: str
    description: str
    duration: str

    model_config = ConfigDict(from_attributes=True)


class QuestionBase(BaseModel):
    question: str
    options: List[str]
    correct_answer: Union[int, List[int]]
    type: QuestionType
    justification: str
    difficulty: Optional[DifficultyLevel] = DifficultyLevel.MEDIUM
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    time_limit: Optional[int] = 120  # seconds
    points: Optional[int] = 10
    explanation: Optional[str] = None
    hints: Optional[List[str]] = []
    screenshots: Optional[List[str]] = []


class QuestionCreate(QuestionBase):
    quiz_set_id: str
    reference_links: Optional[List[ReferenceLink]] = []
    videos: Optional[List[VideoResource]] = []


class QuestionUpdate(BaseModel):
    question: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[Union[int, List[int]]] = None
    type: Optional[QuestionType] = None
    justification: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    time_limit: Optional[int] = None
    points: Optional[int] = None
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    screenshots: Optional[List[str]] = None
    reference_links: Optional[List[ReferenceLink]] = None
    videos: Optional[List[VideoResource]] = None


class Question(QuestionBase):
    id: str
    quiz_set_id: str
    reference_links: List[ReferenceLink] = []
    videos: List[VideoResource] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    review_status: Optional[str] = "pending"
    difficulty_rating: Optional[float] = None
    success_rate: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class QuizSetBase(BaseModel):
    title: str
    description: str
    category: str
    difficulty: DifficultyLevel
    estimated_time: int  # minutes
    is_active: Optional[bool] = True


class QuizSetCreate(QuizSetBase):
    pass


class QuizSetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    estimated_time: Optional[int] = None
    is_active: Optional[bool] = None


class QuizSet(QuizSetBase):
    id: str
    total_questions: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class QuizSetWithQuestions(QuizSet):
    questions: List[Question] = []


class UserProgressBase(BaseModel):
    quiz_set_id: str
    current_question: int = 0
    answers: Dict[str, Union[int, List[int]]] = {}
    score: float = 0.0
    time_spent: int = 0  # seconds


class UserProgressCreate(UserProgressBase):
    user_id: str


class UserProgressUpdate(BaseModel):
    current_question: Optional[int] = None
    answers: Optional[Dict[str, Union[int, List[int]]]] = None
    score: Optional[float] = None
    time_spent: Optional[int] = None
    completed_at: Optional[datetime] = None


class UserProgress(UserProgressBase):
    id: str
    user_id: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class QuizSubmission(BaseModel):
    answers: Dict[str, Union[int, List[int]]]


class DetailedResult(BaseModel):
    question_id: str
    correct: bool
    user_answer: Union[int, List[int]]
    correct_answer: Union[int, List[int]]


class QuizResults(BaseModel):
    score: float
    correct_answers: int
    total_questions: int
    time_spent: int
    detailed_results: List[DetailedResult]


class QuestionStats(BaseModel):
    question_id: str
    correct_rate: float
    avg_time_spent: float


class QuizAnalytics(BaseModel):
    total_attempts: int
    average_score: float
    completion_rate: float
    question_stats: List[QuestionStats]


class UserStats(BaseModel):
    total_quizzes: int
    completed_quizzes: int
    average_score: float
    total_time_spent: int
    strong_categories: List[str]
    weak_categories: List[str]


class UserBase(BaseModel):
    name: str
    email: str
    role: Optional[str] = "user"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
