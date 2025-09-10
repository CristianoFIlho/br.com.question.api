from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    progress = relationship("UserProgress", back_populates="user")


class QuizSet(Base):
    __tablename__ = "quiz_sets"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    estimated_time = Column(Integer, nullable=False)  # minutes
    total_questions = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    questions = relationship("Question", back_populates="quiz_set", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="quiz_set")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=generate_uuid)
    quiz_set_id = Column(String, ForeignKey("quiz_sets.id"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of strings
    correct_answer = Column(JSON, nullable=False)  # int or List[int]
    type = Column(String(20), nullable=False)  # radio, checkbox
    justification = Column(Text, nullable=False)
    difficulty = Column(String(20), default="medium")
    category = Column(String(100))
    tags = Column(JSON, default=list)  # List of strings
    time_limit = Column(Integer, default=120)  # seconds
    points = Column(Integer, default=10)
    explanation = Column(Text)
    hints = Column(JSON, default=list)  # List of strings
    screenshots = Column(JSON, default=list)  # List of URLs
    reference_links = Column(JSON, default=list)  # List of ReferenceLink objects
    videos = Column(JSON, default=list)  # List of VideoResource objects
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_updated = Column(DateTime(timezone=True))
    review_status = Column(String(20), default="pending")
    difficulty_rating = Column(Float)
    success_rate = Column(Float)

    # Relationships
    quiz_set = relationship("QuizSet", back_populates="questions")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    quiz_set_id = Column(String, ForeignKey("quiz_sets.id"), nullable=False)
    current_question = Column(Integer, default=0)
    answers = Column(JSON, default=dict)  # Dict[str, Union[int, List[int]]]
    score = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)  # seconds
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="progress")
    quiz_set = relationship("QuizSet", back_populates="progress")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    quiz_set_id = Column(String, ForeignKey("quiz_sets.id"), nullable=False)
    answers = Column(JSON, nullable=False)
    score = Column(Float, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    time_spent = Column(Integer, nullable=False)
    detailed_results = Column(JSON, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    quiz_set = relationship("QuizSet")
