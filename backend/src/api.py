import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

## DB SETUP
db_drop_and_create_all()

## ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
	try:
		drinkList = Drink.query.all()

		return jsonify({
			'success': True,
			'drinks': [drink.short() for drink in drinkList]
		}), 200
	except Exception:
		abort(404)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
	try:
		drinkList = Drink.query.all()
		drinks = [drink.long() for drink in drinkList]

		return jsonify({
			'success': True,
			'drinks': drinks
		}), 200
	except Exception:
		abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(payload):
	body = request.get_json()

	try:
		drinkTitle = body.get('title')
		drinkRecipe = json.dumps(body.get('recipe'))

		newDrink = Drink(
			title = drinkTitle,
			recipe = drinkRecipe
		)

		newDrink.insert()

		return jsonify({
			'success': True,
			'drinks': [newDrink.long()]
		}), 200

	except Exception:
		abort(422)


'''
@TODO implement endpoint
	PATCH /drinks/<id>
		where <id> is the existing model id
		it should respond with a 404 error if <id> is not found
		it should update the corresponding row for <id>
		it should require the 'patch:drinks' permission
		it should contain the drink.long() data representation
	returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
		or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
	DELETE /drinks/<id>
		where <id> is the existing model id
		it should respond with a 404 error if <id> is not found
		it should delete the corresponding row for <id>
		it should require the 'delete:drinks' permission
	returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
		or appropriate status code indicating reason for failure
'''


## Error Handling

@app.errorhandler(400)
def bad_request(error):
	return jsonify({
		"success": False,
		"error": 400,
		"message": "Bad Request"
	}), 400

@app.errorhandler(401)
def unauthorized(error):
	return jsonify({
		"success": False,
		"error": 401,
		"message": "Unauthorized"
	}), 401

@app.errorhandler(404)
def not_found(error):
	return jsonify({
		"success": False,
		"error": 404,
		"message": "Not Found"
	}), 404

@app.errorhandler(422)
def unprocessable(error):
	return jsonify({
		"success": False,
		"error": 422,
		"message": "Unprocessable Entity"
	}), 422