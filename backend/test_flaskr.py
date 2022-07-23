import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        # self.database_name = "trivia_test"
        self.database_path = os.environ['DATABASE_URL_TEST']
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "Who let the dogs",
            "answer": "Who who who who",
            "category": 2,
            "difficulty": 5
        }

        self.fail_question = {
            "question": None,
            "answer": None,
            "category": None,
            "id": 0
        }

        self.search_term = {"searchTerm": "who", "currentCategory": "Sports"}
        self.quiz_parameter_all = {
            "previous_questions": [],
            "quiz_category": {
                "type": "click",
                "id": 0
            }
        }

        self.quiz_parameter_others = {
            "previous_question": [8, 9],
            "quiz_category": {
                "type": "click",
                "id": 1
            }
        }

        self.quiz_fail = {
            "previous_questions": [10, 11],
            "quiz_category": {
                "type": "click",
                "id": 500
            }
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        print('tearDown')
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paged_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'] is None)

    def test_404_page_to_high(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def test_get_category_questions(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_no_questions_for_category(self):
        res = self.client().get("/categories/115/question")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_404_categories_bad_path(self):
        res = self.client().get("/categories/500")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    # def test_delete_question(self):
    #     res = self.client().delete("/questions/18")
    #     data = json.loads(res.data)
    #     question = Question.query.get(18)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(question, None)

    def test_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_422_question_creation_fails(self):
        res = self.client().post("/questions", json=None)
        data = json.loads(res.data)
        print(res.status_code)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_search_question(self):
        res = self.client().post("/questions/search", json=self.search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'])

    def test_search_term_not_supplied_fails(self):
        res = self.client().post("/questions/search")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")

    def test_get_quiz(self):
        res = self.client().post("/quizzes", json=self.quiz_parameter_all)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_quiz_no_questions_fails(self):
        res = self.client().post("/quizzes", json=self.quiz_fail)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()