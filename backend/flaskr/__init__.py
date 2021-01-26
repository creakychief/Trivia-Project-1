import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def pagination_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    quizzes = [play_quiz.format() for play_quiz in questions]
    current_questions = quizzes[start:end]

    return current_questions


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={"r:*/*": {"origins": "*"}})
    # Set up CORS. Allow '*' for origins. Delete the sample route after
    # Completing the TODOs

    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, DELETE, OPTIONS')
        return response
    # Use the after_request decorator to set Access-Control-Allow

    @app.route('/categories/', methods=['GET'])
    def get_all_categories():
        categories = Category.query.all()
        formatted_category = {category.id:
                              category.type for category in categories}

        return jsonify({
            'categories': formatted_category,
            'status': 200
        })

    # I set up a connection to pull 10 questions into the page

    @app.route('/questions/', methods=['GET'])
    def get_all_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        current_questions = pagination_questions(request, questions)
        formatted_categories = {
            category.id: category.type for category in categories}
        categories = list(map(Category.format, Category.query.all()))

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': formatted_categories,
            'current_category': None
        })

# DELETE method to delete questions

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()

            if not question:
                abort(404)
            question.delete()

            return jsonify({
                'success': True
            })

        except BaseException:
            abort(422)  # 400

# POST method to add questions

    @app.route('/add/', methods=['POST'])
    def create_question():
        request_body = request.get_json()
        question = request_body.get('question', '')
        answer = request_body.get('answer', '')
        category = request_body.get('category', '')
        difficulty = request_body.get('difficulty', '')

        if ((question == '') or (answer == '') or (
                difficulty == '') or (category == '')):
            abort(422)
        try:
            question = Question(question=question, answer=answer,
                                category=category, difficulty=difficulty)
            question.insert()

            questions = Question.query.order_by(Question.id).all()
            current_questions = pagination_questions(request, questions)
            total_questions = len(questions)

            return jsonify({
                'success': True,
                'created': quesiton.id,
                'questions': current_questions,
                'total_question': total_questions,
                'message': 'Question successfully created!'
            }), 200

        except BaseException:
            abort(422)

# POST function to search for questions

    @app.route('/questions/search/', methods=['POST'])
    def search_question():
        try:
            body = request.get_json()
            search = body.get('searchTerm', None)
            results = Question.query.filter(
                Question.question.ilike('%{}%'.format(search))).all()
# Question.query.filter(Question.question.ilike(f'%{search}%')).all()
            formatted_questions = [question.format() for question in results]

            if len(results) == 0:
                # print (sys.exc_info())
                formatted_questions = []
                abort(400)

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                # 'questions': paginate_questions(result, results),
                'total_questions': len(results),
                'current_category': None
            })
        except BaseException:
            abort(404)

# Pull questions via type of category

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        questions = Question.query.filter_by(category=category_id).all()
        formatted_questions = [question.format() for question in questions]
        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': category_id
        })

#

    @app.route('/play/', methods=['POST'])
    def quizzes():
        try:
            data = request.get_json()
# check given category
            category_id = int(data["quiz_category"]["id"])
            category = Category.query.get(category_id)
            previous_questions = data["previous_questions"]
            if not category is None:
                if "previous_questions" in data and len(
                        previous_questions) > 0:
                    questions = Question.query.filter(
                        Question.id.notin_(previous_questions),
                        Question.category == category.id
                    ).all()
                else:
                    questions = Question.query.filter(
                        Question.category == category.id).all()
            else:
                if "previous_questions" in data and len(
                        previous_questions) > 0:
                    questions = Question.query.filter(
                        Question.id.notin_(previous_questions)).all()
                else:
                    questions = Question.query.all()
            max = len(questions) - 1
            if max > 0:
                question = questions[random.randint(0, max)].format()
            else:
                question = False
            return jsonify({
                "success": True,
                "question": question
            })
        except BaseException:
            abort(500,
                  "An error occured while trying to load the next question")

# Create a POST endpoint to get questions to play the quiz.

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "bad request"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(500)
    def restricted(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Error"
        }), 500

    return app
