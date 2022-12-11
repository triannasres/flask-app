from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import pymysql

auth = Blueprint('auth', __name__)
conn = pymysql.connect(
    user="root",
    password="", #GANTI PASSWORDNYA
    host="127.0.0.1",
    port=3306,
    database="tubestst",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

cur = conn.cursor()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cur.execute("SELECT * from users where username = %s", (username))
        user = cur.fetchone()
        print(user)
        if user:
            if(user.pass_hash == password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('username does not exist.', category='error')

    return render_template("login.html", user=current_user)