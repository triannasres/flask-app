from flask import Flask, render_template, session
from flask import jsonify
from flask import request
import pymysql 
import datetime
import pymysql
import jwt
from flask import render_template, request, flash, redirect, url_for
from functools import wraps
import random
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aduhAPIpanas'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)

conn = pymysql.connect(
    user = 'doadmin',
    password = 'AVNS_fq5jSrfRZwgjmjeSQIR',
    host = 'tubes-tst-kelompok-10-k02-do-user-12982385-0.b.db.ondigitalocean.com',
    port = 25060,
    database = 'tubestst',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

cur = conn.cursor()

def token_required(f):
    @wraps(f)
    def token_dec(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return "Missing Token!"
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], ['HS256'])
        except:
            return "Invalid Token"
        return f(*args, **kwargs)
    return token_dec

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/uscovid", methods = ['GET'])
@token_required
def uscovid():
    cur.execute("SELECT * FROM uscovid")
    rv = cur.fetchall()
    return rv

@app.route("/uscovid/state", methods = ['GET'])
@token_required
def statefil():
    sqlQuery = "SELECT * FROM uscovid WHERE state=%s"
    bindData = request.args.get('state')
    cur.execute(sqlQuery, bindData)
    rv = cur.fetchall()
    return rv

@app.route("/uscovid/insert", methods=['POST'])
#http://127.0.0.1:5000/uscovid/insert?date="04-04-2022"&county="Jakarta"&state="DKI"&cases=3
def insertuscovid():
    try:
        sqlQuery = "INSERT INTO uscovid(date, county, state, cases) VALUES(%s, %s, %s, %s)"
        bindData = (request.args.get('date'), 
        request.args.get('county'), 
        request.args.get('state'), 
        request.args.get('cases',type=int))            
        cur.execute(sqlQuery, bindData)
        response = jsonify('Covid data added successfully!')
        response.status_code = 200
        return response
    except Exception as e:
        print(e)    

@app.route("/uscovid/update", methods = ['PUT'])
def updateuscovid():
    try:
        sqlQuery = "UPDATE uscovid SET county=%s, state=%s, cases=%s WHERE date=%s"
        bindData = (request.args.get('county'), 
        request.args.get('state'), 
        request.args.get('cases', type=int), 
        request.args.get('date'))
        cur.execute(sqlQuery, bindData)
        response = jsonify('Covid data updated successfully!')
        response.status_code = 200
        return response
    except Exception as e:
        print(e)

@app.route('/uscovid/delete', methods=['DELETE'])
def deleteuscovid():
    try:		
        sqlQuery = "DELETE from uscovid where county=%s and state=%s"
        bindData = (request.args.get('county'), 
        request.args.get('state'))
        cur.execute(sqlQuery, bindData)
        response = jsonify('Covid data deleted successfully!')
        response.status_code = 200
        return response
    except Exception as e:
        print(e)

@app.route("/uscovid/totalcase", methods = ['GET'])
@token_required
def gettotalcase():
    cur.execute("SELECT county, state, SUM(cases) AS 'Total' from uscovid group by state, county")
    rv = cur.fetchall()
    return rv

@app.route("/uscovid/allocation", methods = ['GET'])
@token_required
def getallocation():
    username = request.args.get('username')
    password = request.args.get('password')
    url = f"https://starfish-app-vepuj.ondigitalocean.app/tubeststkelompok102/login?username={username}&password={password}"
    token = requests.post(url)

    url2 = f"https://starfish-app-vepuj.ondigitalocean.app/tubeststkelompok102/ecommerce/total?token={token.text}"
    result = requests.get(url2)
    totalcase = gettotalcase()
    return result.text + str(totalcase)

@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response  

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "Please provide username and password"

        pass_hash = (password)
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))

        if cur.rowcount > 0:
            return "Username already exist"
        
        cur.execute('INSERT INTO users (username, pass_hash) VALUES (%s, %s)', (username, pass_hash))
        flash("Sign Up successful, please login to get jwt token")
        return redirect('login')
    return render_template('sign-up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            username = request.args.get('username')
            password = request.args.get('password')
            if not username or not password:
                return redirect('getotp')

        cur.execute('SELECT * FROM users WHERE username = %s', (username))
        user = cur.fetchone()
        
        if cur.rowcount > 0:
            if (user['pass_hash'] == password):
                flash('Logged in successfully!', category='success')
                pass_hash = user['pass_hash']
                token = jwt.encode({
                    'username': username,
                    'pass_hash': pass_hash,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                }, app.config['SECRET_KEY']
                )
                return(token)
            else:
                return "Incorrect password"
        else:
            return "User not found"
    return render_template("login.html")

@app.route('/getotp')
def getotp():
    otp = random.randint(100000,999999) 
    session['otp'] = otp
    return redirect(url_for('loginotp'))

@app.route('/loginotp', methods=['GET', 'POST'])
def loginotp():
    otp = session.get('otp', None)
    if request.method == 'POST':
        one = request.form.get('otp')
        if(int(one) == int(otp)):
            token = jwt.encode({
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                }, app.config['SECRET_KEY']
                )
            flash(token)
            return token
        else:
            return "Wrong OTP"
    elif(request.method == "GET"):
        flash(otp)
    return render_template("loginotp.html")


