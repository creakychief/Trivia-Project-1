import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'password', 'localhost:5432', self.database_name) 
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass


    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # self.assertTrue(data['total_quesitons'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        # self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertEqual(res.status_code, 405) 
        self.assertEqual(data['success'], False)


    def test_get_all_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(res.status_code, 405) 
        self.assertEqual(data['success'], False)
        # self.assertTrue(data['current_categories'])
    
    def test_delete_questions(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)
        print(data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_delete_questions_error(self):
        res = self.client().delete('/questions/2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_create_question(self):
        data = {
            'question': 'Are cats cool?',
            'answer': 'yes',
            'category': 5,
            'difficulty': 1
        }
        res = self.client().post('/questions', json=data)
        # self.assertEqual(data['success'], True)

    def test_create_question_error(self):
        data = {
            'question': "who was president in 2012?",
            'difficulty': 1,
            'category': 4

        }
        res = self.client().post('/questions', json=data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(len(res.get_json()['message']), 'bad request')

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'which'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # self.assertEqual(data['total_questions'], 5)

    def test_405_search_question(self):
        data = {"searchTerm": "test"}
        res = self.client().get('/questions/search', json=data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.get_json()['success'], False)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        # self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_get_questions_by_category_error(self):
        res = self.client().get('/categories/b/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        # self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "resource not found")

    def test_quizzes(self):
        data = {
            'quiz_category': {
                'id': 1
            },
            "previous_questions": []
        }
        res = self.client().post('/quizzes', json=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['success'], True)

    def test_500_quizzes(self):
        data = {
            "quiz_category": {
                'id': None
            },
            "previous_questions": []
        }
        res = self.client().post('/quizzes', json=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()['success'], False)
    # Write at least one test for each test for successful operation and for expected errors.

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
