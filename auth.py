from flask import Flask, jsonify, request, make_response, render_template
import jwt
import datetime
from functools import wraps

appFlask = Flask(__name__)
appFlask.config['SECRET_KEY'] = 'aduhAPIpanas'

def token_required(f):
    @wraps(f)
    def token_dec(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return "Missing Token!"
        try:
            data = jwt.decode(token, appFlask.config['SECRET_KEY'])
        except:
            return "Invalid Token"
        return f(*args, **kwargs)
    return token_dec

@appFlask.route('/insecured')
def insecured():
    return "This resource is public. Anyone can access this"

@appFlask.route('/secured')
@token_required
def secured():
    return "You are authenticated to see the resource"

@appFlask.route('/login')
def login():
    userAuth = request.authorization
    if userAuth and userAuth.password == 'secret':
        token = jwt.encode({'user' : userAuth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=1800)}, appFlask.config['SECRET_KEY'])
        return token.decode('UTF-8')
    return "Login Required"

if __name__ == '__main__':
    appFlask.run(debug=True)