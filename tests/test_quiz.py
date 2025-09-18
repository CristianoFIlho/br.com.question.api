"""
Tests for quiz endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.models.database import QuizSet as DBQuizSet, Question as DBQuestion


class TestQuizSets:
    """Test quiz set endpoints"""
    
    def test_get_quiz_sets(self, client):
        """Test getting all quiz sets"""
        response = client.get("/api/v1/quiz-sets")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_quiz_set_unauthorized(self, client):
        """Test creating quiz set without authentication"""
        response = client.post(
            "/api/v1/quiz-sets",
            json={
                "title": "Test Quiz",
                "description": "A test quiz",
                "category": "Test",
                "difficulty": "easy",
                "estimated_time": 10
            }
        )
        
        assert response.status_code == 401
    
    def test_create_quiz_set_success(self, client, auth_headers):
        """Test successful quiz set creation"""
        response = client.post(
            "/api/v1/quiz-sets",
            headers=auth_headers,
            json={
                "title": "Test Quiz",
                "description": "A test quiz",
                "category": "Test",
                "difficulty": "easy",
                "estimated_time": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Quiz"
        assert data["description"] == "A test quiz"
        assert data["category"] == "Test"
        assert data["difficulty"] == "easy"
        assert data["estimated_time"] == 10
        assert data["total_questions"] == 0
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
    
    def test_get_quiz_set_by_id(self, client, db_session, auth_headers):
        """Test getting a specific quiz set"""
        # Create a quiz set first
        quiz_set = DBQuizSet(
            title="Test Quiz",
            description="A test quiz",
            category="Test",
            difficulty="easy",
            estimated_time=10
        )
        db_session.add(quiz_set)
        db_session.commit()
        db_session.refresh(quiz_set)
        
        response = client.get(f"/api/v1/quiz-sets/{quiz_set.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == quiz_set.id
        assert data["title"] == "Test Quiz"
    
    def test_get_quiz_set_not_found(self, client):
        """Test getting non-existent quiz set"""
        response = client.get("/api/v1/quiz-sets/non-existent-id")
        
        assert response.status_code == 404
        assert "Resource not found" in response.json()["detail"]
    
    def test_update_quiz_set(self, client, db_session, auth_headers):
        """Test updating a quiz set"""
        # Create a quiz set first
        quiz_set = DBQuizSet(
            title="Original Title",
            description="Original description",
            category="Test",
            difficulty="easy",
            estimated_time=10
        )
        db_session.add(quiz_set)
        db_session.commit()
        db_session.refresh(quiz_set)
        
        response = client.put(
            f"/api/v1/quiz-sets/{quiz_set.id}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "description": "Updated description"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["id"] == quiz_set.id
    
    def test_delete_quiz_set(self, client, db_session, auth_headers):
        """Test deleting a quiz set"""
        # Create a quiz set first
        quiz_set = DBQuizSet(
            title="To Delete",
            description="This will be deleted",
            category="Test",
            difficulty="easy",
            estimated_time=10
        )
        db_session.add(quiz_set)
        db_session.commit()
        db_session.refresh(quiz_set)
        
        response = client.delete(
            f"/api/v1/quiz-sets/{quiz_set.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/quiz-sets/{quiz_set.id}")
        assert get_response.status_code == 404


class TestQuestions:
    """Test question endpoints"""
    
    def test_get_questions(self, client, db_session):
        """Test getting questions for a quiz set"""
        # Create a quiz set and questions
        quiz_set = DBQuizSet(
            title="Test Quiz",
            description="A test quiz",
            category="Test",
            difficulty="easy",
            estimated_time=10
        )
        db_session.add(quiz_set)
        db_session.commit()
        db_session.refresh(quiz_set)
        
        question = DBQuestion(
            quiz_set_id=quiz_set.id,
            question="What is 2+2?",
            options=["3", "4", "5", "6"],
            correct_answer=1,
            type="radio",
            justification="2+2 equals 4"
        )
        db_session.add(question)
        db_session.commit()
        
        response = client.get(f"/api/v1/quiz-sets/{quiz_set.id}/questions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["question"] == "What is 2+2?"
        assert data[0]["options"] == ["3", "4", "5", "6"]
        assert data[0]["correct_answer"] == 1
    
    def test_create_question_unauthorized(self, client, db_session):
        """Test creating question without authentication"""
        quiz_set = DBQuizSet(
            title="Test Quiz",
            description="A test quiz",
            category="Test",
            difficulty="easy",
            estimated_time=10
        )
        db_session.add(quiz_set)
        db_session.commit()
        db_session.refresh(quiz_set)
        
        response = client.post(
            f"/api/v1/quiz-sets/{quiz_set.id}/questions",
            json={
                "question": "What is 2+2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": 1,
                "type": "radio",
                "justification": "2+2 equals 4"
            }
        )
        
        assert response.status_code == 401
    
    def test_create_question_success(self, client, db_session, auth_headers):
        """Test successful question creation"""
        quiz_set = DBQuizSet(
            title="Test Quiz",
            description="A test quiz",
            category="Test",
            difficulty="easy",
            estimated_time=10
        )
        db_session.add(quiz_set)
        db_session.commit()
        db_session.refresh(quiz_set)
        
        response = client.post(
            f"/api/v1/quiz-sets/{quiz_set.id}/questions",
            headers=auth_headers,
            json={
                "quiz_set_id": quiz_set.id,
                "question": "What is 2+2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": 1,
                "type": "radio",
                "justification": "2+2 equals 4"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "What is 2+2?"
        assert data["options"] == ["3", "4", "5", "6"]
        assert data["correct_answer"] == 1
        assert data["type"] == "radio"
        assert data["justification"] == "2+2 equals 4"
        assert "id" in data
        assert "created_at" in data


class TestQuizSubmission:
    """Test quiz submission endpoints"""
    
    def test_submit_quiz_unauthorized(self, client, db_session):
        """Test submitting quiz without authentication"""
        quiz_set = DBQuizSet(
            title="Test Quiz",
            description="A test quiz",
            category="Test",
            difficulty="easy",
            estimated_time=10
        )
        db_session.add(quiz_set)
        db_session.commit()
        db_session.refresh(quiz_set)
        
        response = client.post(
            f"/api/v1/quiz-sets/{quiz_set.id}/submit",
            json={
                "answers": {}
            }
        )
        
        assert response.status_code == 401
    
    def test_submit_quiz_success(self, client, db_session, auth_headers):
        """Test successful quiz submission"""
        # Create quiz set and questions
        quiz_set = DBQuizSet(
            title="Test Quiz",
            description="A test quiz",
            category="Test",
            difficulty="easy",
            estimated_time=10
        )
        db_session.add(quiz_set)
        db_session.commit()
        db_session.refresh(quiz_set)
        
        question = DBQuestion(
            quiz_set_id=quiz_set.id,
            question="What is 2+2?",
            options=["3", "4", "5", "6"],
            correct_answer=1,
            type="radio",
            justification="2+2 equals 4"
        )
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        response = client.post(
            f"/api/v1/quiz-sets/{quiz_set.id}/submit",
            headers=auth_headers,
            json={
                "answers": {
                    question.id: 1  # Correct answer
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 100.0  # 100% correct
        assert data["correct_answers"] == 1
        assert data["total_questions"] == 1
        assert len(data["detailed_results"]) == 1
        assert data["detailed_results"][0]["correct"] is True
