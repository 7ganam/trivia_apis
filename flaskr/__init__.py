import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
 Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    # CORS Headers

    '''
 Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''

  Create an endpoint to handle GET requests
  for all available categories.
  '''

    def paginate_categories(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        categories = [categorie.format() for categorie in selection]
        current_categories = categories[start:end]
        return current_categories

    @app.route('/categories')
    def retrieve_categories():
        current_categories = {}
        selection = Category.query.order_by(Category.id).all()
        categories = [category.format() for category in selection]
        for category in categories:
            # print(category["id"])
            current_categories[category["id"]] = category["type"]

        if len(selection) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': current_categories,
            'total_categories': len(Category.query.all())
        })

    '''

  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

    QUESTIONS_PER_PAGE = 10

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions

    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        current_categories = {}
        selection = Category.query.order_by(Category.id).all()
        categories = [category.format() for category in selection]
        for category in categories:
            # print(category["id"])
            current_categories[category["id"]] = category["type"]

        selection = Question.query.order_by(Question.id).all()
        # print(selection)
        current_questions = paginate_questions(request, selection)

        # print(current_questions)
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': current_categories,
            'total_questions': len(Question.query.all())
        })

    '''
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                'success': True,
            })

        except:
            abort(422)

    '''
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        question_text = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)
        searchTerm = body.get('searchTerm', None)

        try:

            if searchTerm:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(searchTerm)))
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection.all())
                })

            else:
                question = Question(
                    question=question_text, answer=answer, difficulty=difficulty, category=category)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

        except:
            abort(422)

    '''
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):

        current_category = category_id

        selection = Question.query.filter(
            Question.category == category_id).order_by(Question.id).all()
        if selection is None:
            abort(404)
        total_questions = [question.format() for question in selection]
        current_questions = paginate_questions(request, selection)

        # print(current_questions)
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'current_category': current_category})

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

    @app.route('/quizzes', methods=['POST'])
    def play():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            remaining_questions = Question.query.filter_by(
                category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()
            if (len(remaining_questions) > 0):
                new_question = remaining_questions[random.randrange(
                    0, len(remaining_questions))].format()
            else:
                new_question = None
            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)

    '''
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
