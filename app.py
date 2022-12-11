from flask import Flask, render_template
from flask_mysqldb import MySQL
from flask import jsonify
from flask import request
import pymysql 
import auth
from werkzeug.security import check_password_hash, generate_password_hash
import simplejson
import datetime
import pymysql
import jwt
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aduhAPIpanas'

# conn = pymysql.connect(
#     user="sql6581671",
#     password="NuYPGjXERw", 
#     host="sql6.freemysqlhosting.net",
#     port=3306,
#     database="sql6581671",
#     cursorclass=pymysql.cursors.DictCursor,
#     autocommit=True
# )
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
app.config['SECRET_TOKEN'] = 'aduhAPIpanas'

cur = conn.cursor()

@app.route('/')
def home():
    # try:
    #     validate_token()
    # except Exception as e:
    #     return e.args[0],401
    return render_template('index.html')

@app.route("/ecommerce", methods = ['GET'])
def ecommerce():
    cur.execute("SELECT * FROM ecommerce")
    row_headers=[x[0] for x in cur.description] #this will extract row headers
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return render_template("ecommerce.html",data=jsonify(json_data))

@app.route("/uscovid", methods = ['GET'])
def uscovid():
    cur.execute("SELECT * FROM uscovid")
    row_headers=[x[0] for x in cur.description] #this will extract row headers
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return render_template("ecommerce.html",data=jsonify(json_data))

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cur.execute("SELECT * from users where username = %s", (username))
        user = cur.fetchone()
        print(user)
        if user:
            if(user["pass_hash"] == password):
                flash('Logged in successfully!', category='success')
                return redirect(url_for('ecommerce'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('username does not exist.', category='error')

    return render_template("login.html", user=current_user)        