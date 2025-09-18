"""
Tests for service layer
"""

import pytest
from app.services.quiz_service import QuizService
from app.models.schemas import QuizSetCreate, QuestionCreate, QuizSubmission
from app.models.database import QuizSet as DBQuizSet, Question as DBQuestion


class TestQuizService:
    """Test QuizService functionality"""
    
    def test_create_quiz_set(self, db_session):
        """Test creating a quiz set via service"""
        service = QuizService(db_session)
        
        quiz_set_data = QuizSetCreate(
            title="Service Test Quiz",
            description="A quiz created via service",
            category="Service Test",
            difficulty="medium",
            estimated_time=15
        )
        
        quiz_set = service.create_quiz_set(quiz_set_data)
        
        assert quiz_set.title == "Service Test Quiz"
        assert quiz_set.description == "A quiz created via service"
        assert quiz_set.category == "Service Test"
        assert quiz_set.difficulty == "medium"
        assert quiz_set.estimated_time == 15
        assert quiz_set.total_questions == 0
        assert quiz_set.is_active is True
        assert quiz_set.id is not None
    
    def test_get_quiz_set(self, db_session):
        """Test getting a quiz set via service"""
        service = QuizService(db_session)
        
        # Create a quiz set directly in database
        db_quiz_set = DBQuizSet(
            title="Direct Quiz",
            description="Created directly in DB",
            category="Direct Test",
            difficulty="hard",
            estimated_time=20
        )
        db_session.add(db_quiz_set)
        db_session.commit()
        db_session.refresh(db_quiz_set)
        
        # Get via service
        quiz_set = service.get_quiz_set(db_quiz_set.id)
        
        assert quiz_set is not None
        assert quiz_set.title == "Direct Quiz"
        assert quiz_set.description == "Created directly in DB"
        assert quiz_set.category == "Direct Test"
        assert quiz_set.difficulty == "hard"
        assert quiz_set.estimated_time == 20
    
    def test_create_question(self, db_session):
        """Test creating a question via service"""
        service = QuizService(db_session)
        
        # Create quiz set first
        quiz_set_data = QuizSetCreate(
            title="Question Test Quiz",
            description="A quiz for testing questions",
            category="Question Test",
            difficulty="easy",
            estimated_time=10
        )
        quiz_set = service.create_quiz_set(quiz_set_data)
        
        # Create question
        question_data = QuestionCreate(
            quiz_set_id=quiz_set.id,
            question="What is the capital of France?",
            options=["London", "Berlin", "Paris", "Madrid"],
            correct_answer=2,
            type="radio",
            justification="Paris is the capital of France"
        )
        
        question = service.create_question(question_data)
        
        assert question.question == "What is the capital of France?"
        assert question.options == ["London", "Berlin", "Paris", "Madrid"]
        assert question.correct_answer == 2
        assert question.type == "radio"
        assert question.justification == "Paris is the capital of France"
        assert question.quiz_set_id == quiz_set.id
        assert question.id is not None
        
        # Verify quiz set total_questions was updated
        updated_quiz_set = service.get_quiz_set(quiz_set.id)
        assert updated_quiz_set.total_questions == 1
    
    def test_submit_quiz(self, db_session, test_user):
        """Test quiz submission via service"""
        service = QuizService(db_session)
        
        # Create quiz set and questions
        quiz_set_data = QuizSetCreate(
            title="Submission Test Quiz",
            description="A quiz for testing submissions",
            category="Submission Test",
            difficulty="medium",
            estimated_time=10
        )
        quiz_set = service.create_quiz_set(quiz_set_data)
        
        question_data = QuestionCreate(
            quiz_set_id=quiz_set.id,
            question="What is 3+3?",
            options=["5", "6", "7", "8"],
            correct_answer=1,
            type="radio",
            justification="3+3 equals 6"
        )
        question = service.create_question(question_data)
        
        # Submit quiz
        submission = QuizSubmission(
            answers={question.id: 1}  # Correct answer
        )
        
        results = service.submit_quiz(test_user.id, quiz_set.id, submission)
        
        assert results.score == 100.0
        assert results.correct_answers == 1
        assert results.total_questions == 1
        assert len(results.detailed_results) == 1
        assert results.detailed_results[0].correct is True
        assert results.detailed_results[0].user_answer == 1
        assert results.detailed_results[0].correct_answer == 1
    
    def test_submit_quiz_wrong_answers(self, db_session, test_user):
        """Test quiz submission with wrong answers"""
        service = QuizService(db_session)
        
        # Create quiz set and questions
        quiz_set_data = QuizSetCreate(
            title="Wrong Answers Test Quiz",
            description="A quiz for testing wrong answers",
            category="Wrong Test",
            difficulty="easy",
            estimated_time=5
        )
        quiz_set = service.create_quiz_set(quiz_set_data)
        
        question_data = QuestionCreate(
            quiz_set_id=quiz_set.id,
            question="What is 2+2?",
            options=["3", "4", "5", "6"],
            correct_answer=1,
            type="radio",
            justification="2+2 equals 4"
        )
        question = service.create_question(question_data)
        
        # Submit quiz with wrong answer
        submission = QuizSubmission(
            answers={question.id: 0}  # Wrong answer (3)
        )
        
        results = service.submit_quiz(test_user.id, quiz_set.id, submission)
        
        assert results.score == 0.0
        assert results.correct_answers == 0
        assert results.total_questions == 1
        assert len(results.detailed_results) == 1
        assert results.detailed_results[0].correct is False
        assert results.detailed_results[0].user_answer == 0
        assert results.detailed_results[0].correct_answer == 1
    
    def test_get_quiz_analytics(self, db_session, test_user):
        """Test getting quiz analytics"""
        service = QuizService(db_session)
        
        # Create quiz set
        quiz_set_data = QuizSetCreate(
            title="Analytics Test Quiz",
            description="A quiz for testing analytics",
            category="Analytics Test",
            difficulty="medium",
            estimated_time=10
        )
        quiz_set = service.create_quiz_set(quiz_set_data)
        
        # Create question
        question_data = QuestionCreate(
            quiz_set_id=quiz_set.id,
            question="Test question?",
            options=["A", "B", "C", "D"],
            correct_answer=0,
            type="radio",
            justification="A is correct"
        )
        question = service.create_question(question_data)
        
        # Submit quiz to generate analytics data
        submission = QuizSubmission(
            answers={question.id: 0}  # Correct answer
        )
        service.submit_quiz(test_user.id, quiz_set.id, submission)
        
        # Get analytics
        analytics = service.get_quiz_analytics(quiz_set.id)
        
        assert analytics.total_attempts == 1
        assert analytics.average_score == 100.0
        assert analytics.completion_rate == 1.0
        assert len(analytics.question_stats) == 1
        assert analytics.question_stats[0].question_id == question.id
        assert analytics.question_stats[0].correct_rate == 1.0
    
    def test_get_user_stats(self, db_session, test_user):
        """Test getting user statistics"""
        service = QuizService(db_session)
        
        # Create quiz set
        quiz_set_data = QuizSetCreate(
            title="User Stats Test Quiz",
            description="A quiz for testing user stats",
            category="User Stats Test",
            difficulty="easy",
            estimated_time=5
        )
        quiz_set = service.create_quiz_set(quiz_set_data)
        
        # Create question
        question_data = QuestionCreate(
            quiz_set_id=quiz_set.id,
            question="User stats question?",
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
            correct_answer=1,
            type="radio",
            justification="Option 2 is correct"
        )
        question = service.create_question(question_data)
        
        # Submit quiz
        submission = QuizSubmission(
            answers={question.id: 1}  # Correct answer
        )
        service.submit_quiz(test_user.id, quiz_set.id, submission)
        
        # Get user stats
        stats = service.get_user_stats(test_user.id)
        
        assert stats.total_quizzes == 1
        assert stats.completed_quizzes == 1
        assert stats.average_score == 100.0
        assert stats.total_time_spent == 0  # Default value
        assert "User Stats Test" in stats.strong_categories
