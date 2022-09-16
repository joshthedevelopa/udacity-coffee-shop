from distutils.log import error
from email import message
from functools import wraps
import string
from urllib import response
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        "status": True,
        "drinks": [drink.short() for drink in drinks]
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail", methods=['GET'])
@requires_auth("get:drinks-detail")
def get_drink_details(payload):
    drinks = Drink.query.all()

    return jsonify({
        "status": True,
        "drinks": [drink.long() for drink in drinks]
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['POST'])
@requires_auth("post:drinks")
def add_a_drink(payload):
    data = request.get_json()

    if data is not None and data['title'] is not None and data['recipe'] is not None:
        if bool(data['recipe']) and data['title'].strip() != "":
            if type(data['recipe']) is not list:
                data['recipe'] = [data['recipe']]

            try:
                drink = Drink(
                    title=data['title'],
                    recipe=json.dumps(data['recipe'])
                )

                drink.insert()

                return jsonify({
                    "status": True,
                    "drinks": [drink.long()]
                })

            except:
                abort(
                    422,
                    description="Failed to add drink"
                )

    abort(
        400,
        description="All field are required"
    )



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


@app.route("/drinks/<int:id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def update_a_drink(payload, id):
    data = request.get_json()
    drink = Drink.query.get(id)

    if drink is not None:
        if 'recipe' in data and bool(data['recipe']):
            if type(data['recipe']) is not list:
                data['recipe'] = [data['recipe']]
            
            drink.recipe = json.dumps(data['recipe'])

        if 'title' in data and bool(data['title']):
            drink.title = data['title']

        try:
            drink.update()

            return jsonify({
                "status": True,
                "message": "Drink was udated successfully",
                "drinks": [drink.long()]
            })
        except:
            abort(
                422,
                description="Drink could not be updated"
            )

    abort(
        404,
        description="Drink item does not exist"
    )


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


@app.route("/drinks/<int:id>", methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    drink = Drink.query.get(id)

    if drink is not None:
        try:
            drink.delete()

            return jsonify({
                "status": True,
                "delete": id
            })

        except:
            abort(
                422,
                description="Drink item could not be deleted successfully"
            )

    abort(
        404,
        description="Drink item does not exist"
    )


# Error Handling
'''
Example error handling for unprocessable entity
'''


def error_extraction(error):
    if error is not string and len(str(error).split(":")) == 2:
        return str(error).split(":")[1].strip()

    return error


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": error_extraction(error or "unprocessable")
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
    jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": error_extraction(error or "not_found")
    }), 404



@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": error_extraction(error or "bad_request")
    }), 400

@app.errorhandler(500)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": error_extraction(error or "server_error")
    }), 500

@app.errorhandler(503)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 503,
        "message": error_extraction(error or "server_error")
    }), 503


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_exceptions(error):
    message = error.args[0]
    code = error.args[1]

    return jsonify({
        "success": False,
        "error": code,
        "message": message['description']
    }), code
