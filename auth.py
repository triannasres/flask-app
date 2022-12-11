from flask import Flask, jsonify, request, make_response, render_template, flash, redirect, url_for
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


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
    # userAuth = request.authorization
    # if userAuth and userAuth.password == 'secret':
    #     token = jwt.encode({'user' : userAuth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=1800)}, appFlask.config['SECRET_KEY'])
    #     return token.decode('UTF-8')
    # return "Login Required"

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@appFlask.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@appFlask.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'), role='student')
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

if __name__ == '__main__':
    appFlask.run(debug=True)