import pymysql
import datetime
import pymysql
import jwt
from flask import render_template, request, flash, redirect, url_for, session, jsonify, Flask
from functools import wraps
import random
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'aduhAPIpanas'
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

# conn = pymysql.connect(
#     user="sql6581671",
#     password="NuYPGjXERw", 
#     host="sql6.freemysqlhosting.net",
#     port=3306,
#     database="sql6581671",
#     cursorclass=pymysql.cursors.DictCursor,
#     autocommit=True
# )
# conn = pymysql.connect(
#     user="root",
#     password="", #GANTI PASSWORDNYA
#     host="127.0.0.1",
#     port=3306,
#     database="tubestst",
#     cursorclass=pymysql.cursors.DictCursor,
#     autocommit=True
# )
conn = pymysql.connect(
    user="doadmin",
    password="AVNS_fq5jSrfRZwgjmjeSQIR", 
    host="tubes-tst-kelompok-10-k02-do-user-12982385-0.b.db.ondigitalocean.com",
    port=25060,
    database="tubestst",
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

@app.route("/ecommerce", methods = ['GET'])
@token_required
def ecommerce():
    cur.execute("SELECT * FROM ecommerce")
    rv = cur.fetchall()
    return rv

@app.route("/ecommerce/city", methods = ['GET'])
@token_required
def ecommercecity():
    try:
        city = (request.args.get("city"))
        limit = (request.args.get("limit",type=int))
        sqlQuery = f"select * from ecommerce where city like '%{city}%' limit {limit}"          
        cur.execute(sqlQuery)
        response = cur.fetchall()
        return response    
    except Exception as e:
        print(e)

@app.route("/ecommerce/product", methods = ['GET'])
@token_required
def ecommerceproduct():
    try:
        product = (request.args.get("product"))
        limit = (request.args.get("limit",type=int))
        sqlQuery = f"select * from ecommerce where product like '%{product}%' limit {limit}"        
        cur.execute(sqlQuery)
        response = cur.fetchall()
        return response   
    except Exception as e:
        print(e)    

@app.route("/ecommerce/productcity", methods = ['GET'])
@token_required
def getproductbycity():
    cur.execute("select product, (quantity_ordered*price_each) as total, city from ecommerce group by product, city, total order by product asc")
    rv = cur.fetchall()
    return rv

@app.route("/ecommerce/total", methods = ['GET'])
@token_required
def gettotalecommerce():
    cur.execute("select city, sum(price_each*quantity_ordered) as total from ecommerce group by city order by total desc;")
    rv = cur.fetchall()
    return rv

@app.route("/ecommerce/covidpattern", methods = ['GET'])
@token_required
def getcovidpattern():
    cur.execute("select city, product,quantity_ordered,price_each, sum(cases) FROM ecommerce e join uscovid u ON e.city LIKE '%' || u.county || '%' GROUP BY city, cases, product, price_each, quantity_ordered;;")
    rv = cur.fetchall()
    return rv

@app.route("/ecommerce/covidandcity", methods = ['GET'])
@token_required
def getcovidandcitytotal():
    username = request.args.get("username")
    password = request.args.get("password")
    tokenbembi = request.args.get("token")
    url = f"https://tinidtinidtinid-e9cj4.ondigitalocean.app/tubeststkelompok102/login?username={username}&password={password}"
    token = requests.post(url)
    url2 = f"https://tinidtinidtinid-e9cj4.ondigitalocean.app/tubeststkelompok102/uscovid/totalcase?token={token.text}"
    coviddata = requests.get(url2)
    url4 = f"https://starfish-app-vepuj.ondigitalocean.app/tubeststkelompok102/ecommerce/total?token={tokenbembi}"
    ecommercedata = requests.get(url4)
    return coviddata.text + ecommercedata.text

@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response  

@app.route("/ecommerce/insert", methods=['POST'])
#http://127.0.0.1:5000/ecommerce/insert?order_id=1901&product="AYAM GORENG KUNING"&quantity_ordered=5&price_each=3&city="Jakarta"
@token_required
def insertecommerce():
    try:
        sqlQuery = "INSERT INTO ecommerce(order_id, product, quantity_ordered, price_each, city) VALUES(%s, %s, %s, %s, %s)"
        bindData = (request.args.get('order_id',type=int), 
        request.args.get('product'), 
        request.args.get('quantity_ordered',type=int), 
        request.args.get('price_each',type=int),           
        request.args.get('city'))           
        cur.execute(sqlQuery, bindData)
        response = jsonify('Ecommerce data added successfully!')
        response.status_code = 200
        return response
    except Exception as e:
        print(e)    

@app.route("/ecommerce/update", methods = ['PUT'])
@token_required
def updateecommerce():
    try:
        sqlQuery = "UPDATE ecommerce SET product=%s, quantity_ordered=%s, price_each=%s, city=%s WHERE order_id=%s"
        bindData = (request.args.get('product'), 
        request.args.get('quantity_ordered',type=int), 
        request.args.get('price_each', type=int), 
        request.args.get('city'),
        request.args.get('order_id',type=int))
        cur.execute(sqlQuery, bindData)
        response = jsonify('Ecommerce data updated successfully!')
        response.status_code = 200
        return response
    except Exception as e:
        print(e)

@app.route('/ecommerce/delete', methods=['DELETE'])
@token_required
def deleteecommerce():
    try:		
        sqlQuery = "DELETE from ecommerce where order_id=%s"
        bindData = (request.args.get('order_id',type=int))
        cur.execute(sqlQuery, bindData)
        response = jsonify('Ecommerce deleted successfully!')
        response.status_code = 200
        return response
    except Exception as e:
        print(e)      


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            username = request.args.get('username')
            password = request.args.get('password')

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
    return redirect('loginotp')

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
            return token
        else:
            return "Wrong OTP"
    elif(request.method == "GET"):
        flash(otp)
    return render_template("loginotp.html")
