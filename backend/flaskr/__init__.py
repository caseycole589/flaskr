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
            'success':True,
            'categories': get_formatted_categories()
        })
    """
   
     an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
  
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        current_caterory = request.args.get('currentCategory')
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.all()

        if (len(questions) / 10) + 1 < page:
            abort(404)
        formatted_questions = [question.format() for question in questions]
        return jsonify({
            'success':True,
            'questions':formatted_questions[start:end],
            'total_questions': len(formatted_questions),
            'categories': get_formatted_categories(),
            'current_category': current_caterory if current_caterory != "null" else None
        })
    """
     an endpoint to DELETE question using a question ID.

    
    """
    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question == None:
            abort(422)
        question.delete()
        return jsonify({'success':True})

    """
     an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            parsed = request.get_json()
            question = Question(
                question = parsed['question'],
                answer = parsed['answer'],
                difficulty = parsed['difficulty'],
                category = parsed['category']
            )
            question.insert()
        except Exception as e:
            abort(422)
        return jsonify({'success':True})
    """
    a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    """
    @app.route("/questions/search", methods=['POST'])
    def search_questions():
        try: 
            search_term = request.get_json()['searchTerm']
        except Exception as e:
            abort(400)

        current_caterory = request.get_json()['currentCategory']
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        formatted_questions = [question.format() for question in questions]
        return jsonify({
            'success':True,
            "questions": formatted_questions,
            "total_questions": len(formatted_questions),
            "current_category": current_caterory
        })


    """
    a GET endpoint to get questions based on category.
    """
    @app.route('/categories/<string:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        current_caterory = request.args.get('currentCategory')
        questions = Question.query.filter_by(category=category_id).all()
        formatted_questions = [question.format() for question in questions]
        # there were no questions
        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'success':True,
            'questions':formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': current_caterory
        })
    """
   
    a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

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
        if len(questions) == 0:
            abort(404)
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
            'success':True,
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
            "message": "Bad request"
        }), 400
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "Internal server error"
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
