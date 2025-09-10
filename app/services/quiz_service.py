from typing import List, Optional, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.database import QuizSet as DBQuizSet, Question as DBQuestion, UserProgress as DBUserProgress, QuizAttempt
from app.models.schemas import (
    QuizSetCreate, QuizSetUpdate, QuizSet,
    QuestionCreate, QuestionUpdate, Question,
    UserProgressCreate, UserProgressUpdate, UserProgress,
    QuizSubmission, QuizResults, DetailedResult,
    QuizAnalytics, QuestionStats, UserStats, DifficultyLevel
)
from datetime import datetime
import random


class QuizService:
    def __init__(self, db: Session):
        self.db = db

    def get_quiz_sets(self, skip: int = 0, limit: int = 100) -> List[QuizSet]:
        quiz_sets = (
            self.db.query(DBQuizSet)
            .filter(DBQuizSet.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._convert_quiz_set(qs) for qs in quiz_sets]

    def get_quiz_set(self, quiz_set_id: str) -> Optional[QuizSet]:
        quiz_set = self.db.query(DBQuizSet).filter(DBQuizSet.id == quiz_set_id).first()
        if not quiz_set:
            return None
        return self._convert_quiz_set(quiz_set)

    def create_quiz_set(self, quiz_set_data: QuizSetCreate) -> QuizSet:
        db_quiz_set = DBQuizSet(**quiz_set_data.model_dump())
        self.db.add(db_quiz_set)
        self.db.commit()
        self.db.refresh(db_quiz_set)
        return self._convert_quiz_set(db_quiz_set)

    def update_quiz_set(self, quiz_set_id: str, quiz_set_data: QuizSetUpdate) -> Optional[QuizSet]:
        db_quiz_set = self.db.query(DBQuizSet).filter(DBQuizSet.id == quiz_set_id).first()
        if not db_quiz_set:
            return None
        
        update_data = quiz_set_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_quiz_set, field, value)
        
        self.db.commit()
        self.db.refresh(db_quiz_set)
        return self._convert_quiz_set(db_quiz_set)

    def delete_quiz_set(self, quiz_set_id: str) -> bool:
        db_quiz_set = self.db.query(DBQuizSet).filter(DBQuizSet.id == quiz_set_id).first()
        if not db_quiz_set:
            return False
        
        self.db.delete(db_quiz_set)
        self.db.commit()
        return True

    def get_questions(
        self,
        quiz_set_id: str,
        shuffle: bool = False,
        limit: Optional[int] = None,
        difficulty: Optional[DifficultyLevel] = None
    ) -> List[Question]:
        query = self.db.query(DBQuestion).filter(DBQuestion.quiz_set_id == quiz_set_id)
        
        if difficulty:
            query = query.filter(DBQuestion.difficulty == difficulty.value)
        
        questions = query.all()
        
        if shuffle:
            random.shuffle(questions)
        
        if limit:
            questions = questions[:limit]
        
        return [self._convert_question(q) for q in questions]

    def get_question(self, question_id: str) -> Optional[Question]:
        question = self.db.query(DBQuestion).filter(DBQuestion.id == question_id).first()
        if not question:
            return None
        return self._convert_question(question)

    def create_question(self, question_data: QuestionCreate) -> Question:
        # Convert Pydantic models to dicts for JSON storage
        question_dict = question_data.model_dump()
        reference_links = [link.model_dump() for link in question_data.reference_links]
        videos = [video.model_dump() for video in question_data.videos]
        
        db_question = DBQuestion(
            **{k: v for k, v in question_dict.items() if k not in ['reference_links', 'videos']},
            reference_links=reference_links,
            videos=videos
        )
        
        self.db.add(db_question)
        
        # Update quiz set total questions
        quiz_set = self.db.query(DBQuizSet).filter(DBQuizSet.id == question_data.quiz_set_id).first()
        if quiz_set:
            quiz_set.total_questions += 1
        
        self.db.commit()
        self.db.refresh(db_question)
        return self._convert_question(db_question)

    def update_question(self, question_id: str, question_data: QuestionUpdate) -> Optional[Question]:
        db_question = self.db.query(DBQuestion).filter(DBQuestion.id == question_id).first()
        if not db_question:
            return None
        
        update_data = question_data.model_dump(exclude_unset=True)
        
        # Handle reference_links and videos separately
        if 'reference_links' in update_data:
            update_data['reference_links'] = [link.model_dump() for link in question_data.reference_links or []]
        if 'videos' in update_data:
            update_data['videos'] = [video.model_dump() for video in question_data.videos or []]
        
        for field, value in update_data.items():
            setattr(db_question, field, value)
        
        db_question.last_updated = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_question)
        return self._convert_question(db_question)

    def delete_question(self, question_id: str) -> bool:
        db_question = self.db.query(DBQuestion).filter(DBQuestion.id == question_id).first()
        if not db_question:
            return False
        
        quiz_set_id = db_question.quiz_set_id
        self.db.delete(db_question)
        
        # Update quiz set total questions
        quiz_set = self.db.query(DBQuizSet).filter(DBQuizSet.id == quiz_set_id).first()
        if quiz_set and quiz_set.total_questions > 0:
            quiz_set.total_questions -= 1
        
        self.db.commit()
        return True

    def save_progress(self, user_id: str, progress_data: UserProgressCreate) -> UserProgress:
        # Check if progress already exists
        existing_progress = (
            self.db.query(DBUserProgress)
            .filter(
                DBUserProgress.user_id == user_id,
                DBUserProgress.quiz_set_id == progress_data.quiz_set_id
            )
            .first()
        )
        
        if existing_progress:
            # Update existing progress
            update_data = progress_data.model_dump(exclude={'user_id'})
            for field, value in update_data.items():
                setattr(existing_progress, field, value)
            db_progress = existing_progress
        else:
            # Create new progress
            db_progress = DBUserProgress(user_id=user_id, **progress_data.model_dump(exclude={'user_id'}))
            self.db.add(db_progress)
        
        self.db.commit()
        self.db.refresh(db_progress)
        return self._convert_user_progress(db_progress)

    def get_progress(self, user_id: str, quiz_set_id: str) -> Optional[UserProgress]:
        progress = (
            self.db.query(DBUserProgress)
            .filter(
                DBUserProgress.user_id == user_id,
                DBUserProgress.quiz_set_id == quiz_set_id
            )
            .first()
        )
        if not progress:
            return None
        return self._convert_user_progress(progress)

    def submit_quiz(self, user_id: str, quiz_set_id: str, submission: QuizSubmission) -> QuizResults:
        # Get questions
        questions = self.db.query(DBQuestion).filter(DBQuestion.quiz_set_id == quiz_set_id).all()
        
        detailed_results = []
        correct_answers = 0
        
        for question in questions:
            user_answer = submission.answers.get(question.id)
            correct_answer = question.correct_answer
            
            if user_answer is not None:
                # Check if answer is correct
                if isinstance(correct_answer, list):
                    # Multiple choice
                    user_answer_list = user_answer if isinstance(user_answer, list) else [user_answer]
                    correct = (
                        len(user_answer_list) == len(correct_answer) and
                        all(ans in correct_answer for ans in user_answer_list)
                    )
                else:
                    # Single choice
                    correct = user_answer == correct_answer
                
                if correct:
                    correct_answers += 1
                
                detailed_results.append(DetailedResult(
                    question_id=question.id,
                    correct=correct,
                    user_answer=user_answer,
                    correct_answer=correct_answer
                ))
        
        score = (correct_answers / len(questions)) * 100 if questions else 0
        
        # Save attempt to database
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_set_id=quiz_set_id,
            answers=submission.answers,
            score=score,
            correct_answers=correct_answers,
            total_questions=len(questions),
            time_spent=0,  # TODO: Get from frontend
            detailed_results=[dr.model_dump() for dr in detailed_results]
        )
        self.db.add(attempt)
        
        # Update progress as completed
        progress = (
            self.db.query(DBUserProgress)
            .filter(
                DBUserProgress.user_id == user_id,
                DBUserProgress.quiz_set_id == quiz_set_id
            )
            .first()
        )
        if progress:
            progress.completed_at = datetime.utcnow()
            progress.score = score
        
        self.db.commit()
        
        return QuizResults(
            score=score,
            correct_answers=correct_answers,
            total_questions=len(questions),
            time_spent=0,  # TODO: Calculate from progress
            detailed_results=detailed_results
        )

    def get_quiz_analytics(self, quiz_set_id: str) -> QuizAnalytics:
        # Get all attempts for this quiz set
        attempts = (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.quiz_set_id == quiz_set_id)
            .all()
        )
        
        if not attempts:
            return QuizAnalytics(
                total_attempts=0,
                average_score=0.0,
                completion_rate=0.0,
                question_stats=[]
            )
        
        total_attempts = len(attempts)
        average_score = sum(attempt.score for attempt in attempts) / total_attempts
        
        # Calculate completion rate (users who completed vs started)
        completed_attempts = len([a for a in attempts if a.completed_at])
        completion_rate = completed_attempts / total_attempts if total_attempts > 0 else 0
        
        # Question statistics
        questions = self.db.query(DBQuestion).filter(DBQuestion.quiz_set_id == quiz_set_id).all()
        question_stats = []
        
        for question in questions:
            correct_count = 0
            total_answers = 0
            
            for attempt in attempts:
                detailed_results = attempt.detailed_results
                for result in detailed_results:
                    if result.get('question_id') == question.id:
                        total_answers += 1
                        if result.get('correct'):
                            correct_count += 1
            
            correct_rate = correct_count / total_answers if total_answers > 0 else 0
            question_stats.append(QuestionStats(
                question_id=question.id,
                correct_rate=correct_rate,
                avg_time_spent=60.0  # TODO: Calculate from actual data
            ))
        
        return QuizAnalytics(
            total_attempts=total_attempts,
            average_score=average_score,
            completion_rate=completion_rate,
            question_stats=question_stats
        )

    def get_user_stats(self, user_id: str) -> UserStats:
        # Get user attempts
        attempts = (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.user_id == user_id)
            .all()
        )
        
        if not attempts:
            return UserStats(
                total_quizzes=0,
                completed_quizzes=0,
                average_score=0.0,
                total_time_spent=0,
                strong_categories=[],
                weak_categories=[]
            )
        
        total_quizzes = len(set(attempt.quiz_set_id for attempt in attempts))
        completed_quizzes = len(attempts)
        average_score = sum(attempt.score for attempt in attempts) / completed_quizzes
        total_time_spent = sum(attempt.time_spent for attempt in attempts)
        
        # Calculate category performance
        category_scores = {}
        for attempt in attempts:
            quiz_set = self.db.query(DBQuizSet).filter(DBQuizSet.id == attempt.quiz_set_id).first()
            if quiz_set:
                category = quiz_set.category
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(attempt.score)
        
        # Calculate average per category
        category_averages = {
            cat: sum(scores) / len(scores)
            for cat, scores in category_scores.items()
        }
        
        # Sort by performance
        sorted_categories = sorted(category_averages.items(), key=lambda x: x[1], reverse=True)
        
        strong_categories = [cat for cat, score in sorted_categories[:3] if score >= 70]
        weak_categories = [cat for cat, score in sorted_categories[-3:] if score < 70]
        
        return UserStats(
            total_quizzes=total_quizzes,
            completed_quizzes=completed_quizzes,
            average_score=average_score,
            total_time_spent=total_time_spent,
            strong_categories=strong_categories,
            weak_categories=weak_categories
        )

    def _convert_quiz_set(self, db_quiz_set: DBQuizSet) -> QuizSet:
        return QuizSet(
            id=db_quiz_set.id,
            title=db_quiz_set.title,
            description=db_quiz_set.description,
            category=db_quiz_set.category,
            difficulty=db_quiz_set.difficulty,
            estimated_time=db_quiz_set.estimated_time,
            total_questions=db_quiz_set.total_questions,
            is_active=db_quiz_set.is_active,
            created_at=db_quiz_set.created_at,
            updated_at=db_quiz_set.updated_at
        )

    def _convert_question(self, db_question: DBQuestion) -> Question:
        from app.models.schemas import ReferenceLink, VideoResource
        
        # Convert JSON back to Pydantic models
        reference_links = [
            ReferenceLink(**link) for link in (db_question.reference_links or [])
        ]
        videos = [
            VideoResource(**video) for video in (db_question.videos or [])
        ]
        
        return Question(
            id=db_question.id,
            quiz_set_id=db_question.quiz_set_id,
            question=db_question.question,
            options=db_question.options,
            correct_answer=db_question.correct_answer,
            type=db_question.type,
            justification=db_question.justification,
            difficulty=db_question.difficulty,
            category=db_question.category,
            tags=db_question.tags or [],
            time_limit=db_question.time_limit,
            points=db_question.points,
            explanation=db_question.explanation,
            hints=db_question.hints or [],
            screenshots=db_question.screenshots or [],
            reference_links=reference_links,
            videos=videos,
            created_at=db_question.created_at,
            updated_at=db_question.updated_at,
            last_updated=db_question.last_updated,
            review_status=db_question.review_status,
            difficulty_rating=db_question.difficulty_rating,
            success_rate=db_question.success_rate
        )

    def _convert_user_progress(self, db_progress: DBUserProgress) -> UserProgress:
        return UserProgress(
            id=db_progress.id,
            user_id=db_progress.user_id,
            quiz_set_id=db_progress.quiz_set_id,
            current_question=db_progress.current_question,
            answers=db_progress.answers or {},
            score=db_progress.score,
            time_spent=db_progress.time_spent,
            completed_at=db_progress.completed_at,
            created_at=db_progress.created_at,
            updated_at=db_progress.updated_at
        )
