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
        self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
        DB_NAME = os.getenv('DB_NAME', 'trivia')

        self.database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format(
            DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)

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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        # self.assertEqual(len(data['categories']), 10)

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'], True)
        # print(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_get_paginated_questions_by_category(self):
        res = self.client().get('/categories/1/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'], True)
        # print(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_get_paginated_questions_by_category_no_result(self):
        res = self.client().get('/categories/1333/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def delete_question_by_id_success(self):
        res = self.client().delete('/questions/12')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def delete_question_by_id_fail(self):
        res = self.client().delete('/questions/12000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_new_question(self):
        from random import choice
        import string

        def GenPasswd2(length=8, chars=string.ascii_letters + string.digits):
            return ''.join([choice(chars) for i in range(length)])
        random_text = GenPasswd2(8, string.digits) + \
            GenPasswd2(15, string.ascii_letters)

        new_question = {
            'question': random_text,
            'answer': 'Neil Gaiman',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        question = Question.query.filter(
            Question.question == random_text).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(question)

    def test_get_question_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'was'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 4)

    def test_get_question_search_without_results(self):
        res = self.client().post(
            '/questions', json={'searchTerm': 'applejacks'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)

    def test_quiz_success(self):
        body_object = {"previous_questions": [
            4], "quiz_category": {"type": "Entertainment", "id": "5"}}

        res = self.client().post('/quizzes', json=body_object)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
