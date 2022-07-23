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
   

    """
    Set up CORS. Allow '*' for origins.
    """
    CORS(app, resources={r"/*": {"origins": "*"}})
    
   
    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, DELETE')
        return response

    """
    endpoint to handle GET requests for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        return jsonify({
            'categories': get_formatted_categories()
        })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        current_caterory = request.args.get('currentCategory')
        print(current_caterory)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        return jsonify({
            'questions':formatted_questions[start:end],
            'total_questions': len(formatted_questions),
            'categories': get_formatted_categories(),
            'current_category': current_caterory if current_caterory != "null" else None
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        Question.query.get(question_id).delete()
        return jsonify(success=True)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        parsed = request.get_json()
        question = Question(
            question = parsed['question'],
            answer = parsed['answer'],
            difficulty = parsed['difficulty'],
            category = parsed['category']
        )
        question.insert()
        return jsonify(success=True) 
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=['POST'])
    def search_questions():
        search_term = request.get_json()['searchTerm']
        current_caterory = request.get_json()['currentCategory']
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        formatted_questions = [question.format() for question in questions]
        return jsonify({
            "questions": formatted_questions,
            "totalQuestions": len(formatted_questions),
            "currentCategory": current_caterory
        })


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<string:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        current_caterory = request.args.get('currentCategory')
        questions = Question.query.filter_by(category=category_id).all()
        formatted_questions = [question.format() for question in questions]
        return jsonify({
            'questions':formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': current_caterory
        })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=['POST'])
    def get_quizzes():
        parsed = request.get_json()
        quiz_category = parsed['quiz_category']
        previous_questions =parsed['previous_questions']
        if(quiz_category['id'] == 0):
            questions = Question.query.all()
        else: 
            questions = Question.query.filter(Question.category == str(quiz_category['id'])).all()
        questions_formatted = [question.format() for question in questions]
        # filter out questions already seen
        filtered_questions_formatted = list(filter(lambda x: x['id'] not in previous_questions, questions_formatted))
        # make sure we have a question
        if len(filtered_questions_formatted) > 0:
            # make the question random
            question = filtered_questions_formatted[random.randint(0,len(filtered_questions_formatted)) - 1]
        else: 
            question = None
        return jsonify({
            'previousQuestions': previous_questions,
            'question': question
        })
    """
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Unprocessable"
        }), 422 

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "bad request"
        }), 400
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "internal server error"
        }), 500
        
    return app

def get_formatted_categories():
    categories = Category.query.all()
    categories_formatted = {}
    # make a dictionary for the categories its the datatype the font end wants
    for cat in categories:
        formatted = cat.format()
        categories_formatted[formatted['id']] = formatted['type'] 
    return categories_formatted 
