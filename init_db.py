from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.models.database import Base, QuizSet as DBQuizSet, Question as DBQuestion
from app.models.schemas import DifficultyLevel, QuestionType


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def seed_data():
    """Seed the database with sample data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_quiz_set = db.query(DBQuizSet).filter(DBQuizSet.id == "mcpa-level-1").first()
        if existing_quiz_set:
            print("Sample data already exists. Skipping seed.")
            return
        
        # Create MCPA Level 1 Quiz Set
        mcpa_quiz_set = DBQuizSet(
            id="mcpa-level-1",
            title="MCPA - LEVEL 1 (Training platform)",
            description="MuleSoft Certified Platform Architect - Level 1",
            category="MuleSoft",
            difficulty=DifficultyLevel.MEDIUM.value,
            estimated_time=10,  # 10 minutes
            total_questions=5,
            is_active=True
        )
        db.add(mcpa_quiz_set)
        
        # Sample questions
        questions = [
            {
                "id": "mcpa-1",
                "quiz_set_id": "mcpa-level-1",
                "question": "What is the primary purpose of MuleSoft's Anypoint Platform?",
                "options": [
                    "To create mobile applications",
                    "To connect applications, data, and devices",
                    "To manage database schemas",
                    "To design user interfaces"
                ],
                "correct_answer": 1,
                "type": QuestionType.RADIO.value,
                "justification": "MuleSoft's Anypoint Platform is primarily designed to connect applications, data, and devices across on-premises and cloud environments through APIs and integrations.",
                "difficulty": DifficultyLevel.EASY.value,
                "category": "Platform Overview",
                "tags": ["anypoint", "platform", "integration"],
                "time_limit": 120,
                "points": 10,
                "hints": [
                    "Think about what MuleSoft is known for in the integration space",
                    "Consider the core purpose of an integration platform"
                ],
                "reference_links": [
                    {
                        "title": "Anypoint Platform Overview",
                        "url": "https://docs.mulesoft.com/general/",
                        "description": "Official documentation about Anypoint Platform"
                    }
                ],
                "videos": [
                    {
                        "title": "Introduction to Anypoint Platform",
                        "url": "https://www.youtube.com/watch?v=example",
                        "description": "Overview of MuleSoft Anypoint Platform capabilities",
                        "duration": "10:30"
                    }
                ]
            },
            {
                "id": "mcpa-2",
                "quiz_set_id": "mcpa-level-1",
                "question": "Which of the following are key components of API-led connectivity? (Select all that apply)",
                "options": [
                    "System APIs",
                    "Process APIs", 
                    "Experience APIs",
                    "Database APIs"
                ],
                "correct_answer": [0, 1, 2],
                "type": QuestionType.CHECKBOX.value,
                "justification": "API-led connectivity consists of three layers: System APIs (unlock data from systems), Process APIs (orchestrate data), and Experience APIs (provide data for specific experiences). Database APIs is not a standard layer in this approach.",
                "difficulty": DifficultyLevel.MEDIUM.value,
                "category": "API Design",
                "tags": ["api-led", "connectivity", "architecture"],
                "time_limit": 180,
                "points": 15,
                "hints": [
                    "Think about the three-layer approach in API-led connectivity",
                    "Consider which APIs interact directly with backend systems vs. user experiences"
                ],
                "reference_links": [
                    {
                        "title": "API-led Connectivity",
                        "url": "https://www.mulesoft.com/resources/api/what-is-api-led-connectivity",
                        "description": "Learn about the three-layer API approach"
                    }
                ],
                "videos": []
            },
            {
                "id": "mcpa-3",
                "quiz_set_id": "mcpa-level-1",
                "question": "What is the main benefit of using DataWeave in MuleSoft?",
                "options": [
                    "To create user interfaces",
                    "To transform data between different formats",
                    "To manage API security",
                    "To monitor application performance"
                ],
                "correct_answer": 1,
                "type": QuestionType.RADIO.value,
                "justification": "DataWeave is MuleSoft's expression language designed for data transformation. It allows developers to transform data from one format to another (JSON, XML, CSV, etc.) with powerful mapping capabilities.",
                "difficulty": DifficultyLevel.EASY.value,
                "category": "Data Transformation",
                "tags": ["dataweave", "transformation", "mapping"],
                "time_limit": 90,
                "points": 10,
                "hints": [
                    "DataWeave is specifically designed for one primary purpose",
                    "Think about what happens when data moves between different systems"
                ],
                "reference_links": [
                    {
                        "title": "DataWeave Language",
                        "url": "https://docs.mulesoft.com/dataweave/",
                        "description": "Complete guide to DataWeave transformation language"
                    }
                ],
                "videos": [
                    {
                        "title": "DataWeave Fundamentals",
                        "url": "https://www.youtube.com/watch?v=dataweave-example",
                        "description": "Learn the basics of DataWeave transformations",
                        "duration": "15:45"
                    }
                ]
            },
            {
                "id": "mcpa-4",
                "quiz_set_id": "mcpa-level-1",
                "question": "In Anypoint Studio, what is a Connector?",
                "options": [
                    "A tool for debugging applications",
                    "A pre-built component that connects to external systems",
                    "A security mechanism for APIs",
                    "A performance monitoring tool"
                ],
                "correct_answer": 1,
                "type": QuestionType.RADIO.value,
                "justification": "Connectors in Anypoint Studio are pre-built components that facilitate connections to external systems, databases, and services. They provide standardized ways to interact with various systems without writing custom integration code.",
                "difficulty": DifficultyLevel.EASY.value,
                "category": "Development Tools",
                "tags": ["connectors", "studio", "integration"],
                "time_limit": 90,
                "points": 10,
                "hints": [
                    "Think about how MuleSoft simplifies connections to external systems",
                    "Consider pre-built vs. custom integration components"
                ],
                "reference_links": [
                    {
                        "title": "Anypoint Connectors",
                        "url": "https://docs.mulesoft.com/connectors/",
                        "description": "Documentation for all available MuleSoft connectors"
                    }
                ],
                "videos": []
            },
            {
                "id": "mcpa-5",
                "quiz_set_id": "mcpa-level-1",
                "question": "What is the primary purpose of API Manager in Anypoint Platform?",
                "options": [
                    "To design and build APIs",
                    "To govern, secure, and monitor APIs",
                    "To transform data formats",
                    "To create user documentation"
                ],
                "correct_answer": 1,
                "type": QuestionType.RADIO.value,
                "justification": "API Manager is the component of Anypoint Platform responsible for API governance, security, and monitoring. It handles policies, SLA tiers, analytics, and overall API lifecycle management.",
                "difficulty": DifficultyLevel.MEDIUM.value,
                "category": "API Management",
                "tags": ["api-manager", "governance", "security"],
                "time_limit": 120,
                "points": 12,
                "hints": [
                    "Think about what happens after APIs are built",
                    "Consider the operational aspects of API lifecycle"
                ],
                "reference_links": [
                    {
                        "title": "API Manager Overview",
                        "url": "https://docs.mulesoft.com/api-manager/",
                        "description": "Learn about API governance and management capabilities"
                    }
                ],
                "videos": [
                    {
                        "title": "API Manager Deep Dive",
                        "url": "https://www.youtube.com/watch?v=api-manager-example",
                        "description": "Complete overview of API Manager features",
                        "duration": "20:15"
                    }
                ]
            }
        ]
        
        # Add questions to database
        for question_data in questions:
            db_question = DBQuestion(**question_data)
            db.add(db_question)
        
        db.commit()
        print("Sample data seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Tables created successfully!")
    
    print("Seeding sample data...")
    seed_data()
    print("Database initialization complete!")
