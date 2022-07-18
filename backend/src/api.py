import os
import sys
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth 

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()


# # ROUTES
# Get drinks endpoint
@app.route('/drinks')
def get_all_drinks():
    drinks = Drink.query.all()
    return jsonify({"success": True, 
    "drinks": [drink.short() for drink in drinks]
    })
# Get drink details
@app.route('/drinks-details')
@requires_auth("get:drinks-details")
def get_drinks_details(payload):
    drinks = Drink.query.all()

    return jsonify({"success": True, 
    "drinks": [drink.long() for drink in drinks]
    })


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def create_new_drink(payload):
    body = request.get_json()
    new_title = body['title']
    new_recipe = json.dumps(body['recipe'])
    try:
        new_drink = Drink(title=new_title, recipe=new_recipe)
        new_drink.insert()
    except Exception:
        abort(500)
    return jsonify({
        'sucess': True,
        'drink': [new_drink.long()]
    })

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    updated_title = body.get('title')
    updated_recipe = body.get('recipe')
    
    if drink is None:
        abort(404)
    try:
        if updated_title:
            drink.title = updated_title

        elif updated_recipe:
            drink.recipe = json.dumps(updated_recipe)
        else: 
            abort(400)

        drink.update()
    except Exception:
        abort(500)
    return jsonify({
        'success': True,
        'drink': [drink.long()]
    })

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    try:
        drink.delete()
    except Exception:
        abort(500)
    return jsonify({
        'success': True,
        'drink id': id
    })
# Error Handling
@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def auth_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def auth_error(error):
    print(error)
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Server error'
    }),  500

@app.errorhandler(405)
def auth_error(error):
    print(error)
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
    }),  405

@app.errorhandler(AuthError)
def auth_error(error):
    print(error)
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }),  error.status_code