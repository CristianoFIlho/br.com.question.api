from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.quiz_service import QuizService
from app.models.schemas import (
    QuizSet, QuizSetCreate, QuizSetUpdate,
    Question, QuestionCreate, QuestionUpdate,
    UserProgress, UserProgressCreate, UserProgressUpdate,
    QuizSubmission, QuizResults, QuizAnalytics, UserStats,
    DifficultyLevel
)
from app.routers.auth import get_current_active_user
from app.models.database import User as DBUser

router = APIRouter()


@router.get("/quiz-sets", response_model=List[QuizSet])
async def get_quiz_sets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all quiz sets"""
    service = QuizService(db)
    return service.get_quiz_sets(skip=skip, limit=limit)


@router.get("/quiz-sets/{quiz_set_id}", response_model=QuizSet)
async def get_quiz_set(quiz_set_id: str, db: Session = Depends(get_db)):
    """Get a specific quiz set"""
    service = QuizService(db)
    quiz_set = service.get_quiz_set(quiz_set_id)
    if not quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set not found")
    return quiz_set


@router.post("/quiz-sets", response_model=QuizSet)
async def create_quiz_set(
    quiz_set: QuizSetCreate, 
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Create a new quiz set (requires authentication)"""
    service = QuizService(db)
    return service.create_quiz_set(quiz_set)


@router.put("/quiz-sets/{quiz_set_id}", response_model=QuizSet)
async def update_quiz_set(
    quiz_set_id: str, 
    quiz_set: QuizSetUpdate, 
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Update a quiz set (requires authentication)"""
    service = QuizService(db)
    updated_quiz_set = service.update_quiz_set(quiz_set_id, quiz_set)
    if not updated_quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set not found")
    return updated_quiz_set


@router.delete("/quiz-sets/{quiz_set_id}")
async def delete_quiz_set(
    quiz_set_id: str, 
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Delete a quiz set (requires authentication)"""
    service = QuizService(db)
    success = service.delete_quiz_set(quiz_set_id)
    if not success:
        raise HTTPException(status_code=404, detail="Quiz set not found")
    return {"message": "Quiz set deleted successfully"}


@router.get("/quiz-sets/{quiz_set_id}/questions", response_model=List[Question])
async def get_questions(
    quiz_set_id: str,
    shuffle: bool = Query(False),
    limit: Optional[int] = Query(None, ge=1),
    difficulty: Optional[DifficultyLevel] = Query(None),
    db: Session = Depends(get_db)
):
    """Get questions for a quiz set"""
    service = QuizService(db)
    
    # Verify quiz set exists
    quiz_set = service.get_quiz_set(quiz_set_id)
    if not quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set not found")
    
    return service.get_questions(
        quiz_set_id=quiz_set_id,
        shuffle=shuffle,
        limit=limit,
        difficulty=difficulty
    )


@router.get("/quiz-sets/{quiz_set_id}/questions/{question_id}", response_model=Question)
async def get_question(
    quiz_set_id: str, 
    question_id: str, 
    db: Session = Depends(get_db)
):
    """Get a specific question"""
    service = QuizService(db)
    question = service.get_question(question_id)
    if not question or question.quiz_set_id != quiz_set_id:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.post("/quiz-sets/{quiz_set_id}/questions", response_model=Question)
async def create_question(
    quiz_set_id: str,
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Create a new question (requires authentication)"""
    service = QuizService(db)
    
    # Verify quiz set exists
    quiz_set = service.get_quiz_set(quiz_set_id)
    if not quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set not found")
    
    # Set quiz_set_id in question data
    question.quiz_set_id = quiz_set_id
    return service.create_question(question)


@router.put("/quiz-sets/{quiz_set_id}/questions/{question_id}", response_model=Question)
async def update_question(
    quiz_set_id: str,
    question_id: str,
    question: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Update a question (requires authentication)"""
    service = QuizService(db)
    
    # Verify question exists and belongs to quiz set
    existing_question = service.get_question(question_id)
    if not existing_question or existing_question.quiz_set_id != quiz_set_id:
        raise HTTPException(status_code=404, detail="Question not found")
    
    updated_question = service.update_question(question_id, question)
    if not updated_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated_question


@router.delete("/quiz-sets/{quiz_set_id}/questions/{question_id}")
async def delete_question(
    quiz_set_id: str,
    question_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Delete a question (requires authentication)"""
    service = QuizService(db)
    
    # Verify question exists and belongs to quiz set
    existing_question = service.get_question(question_id)
    if not existing_question or existing_question.quiz_set_id != quiz_set_id:
        raise HTTPException(status_code=404, detail="Question not found")
    
    success = service.delete_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}


@router.post("/quiz-sets/{quiz_set_id}/submit", response_model=QuizResults)
async def submit_quiz(
    quiz_set_id: str,
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Submit quiz answers and get results"""
    service = QuizService(db)
    
    # Verify quiz set exists
    quiz_set = service.get_quiz_set(quiz_set_id)
    if not quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set not found")
    
    return service.submit_quiz(current_user.id, quiz_set_id, submission)


@router.post("/progress", response_model=UserProgress)
async def save_progress(
    progress: UserProgressCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Save user progress"""
    service = QuizService(db)
    return service.save_progress(current_user.id, progress)


@router.get("/progress/{quiz_set_id}", response_model=UserProgress)
async def get_progress(
    quiz_set_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get user progress for a quiz set"""
    service = QuizService(db)
    progress = service.get_progress(current_user.id, quiz_set_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    return progress


@router.get("/quiz-sets/{quiz_set_id}/analytics", response_model=QuizAnalytics)
async def get_quiz_analytics(quiz_set_id: str, db: Session = Depends(get_db)):
    """Get analytics for a quiz set"""
    service = QuizService(db)
    
    # Verify quiz set exists
    quiz_set = service.get_quiz_set(quiz_set_id)
    if not quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set not found")
    
    return service.get_quiz_analytics(quiz_set_id)


@router.get("/users/stats", response_model=UserStats)
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get user statistics"""
    service = QuizService(db)
    return service.get_user_stats(current_user.id)
