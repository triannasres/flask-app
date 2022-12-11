from flask import Flask, Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from flask_mysqldb import MySQL
from flask import jsonify
from flask import request
import pymysql
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql

conn = pymysql.connect(
    user="root",
    password="", #GANTI PASSWORDNYA
    host="127.0.0.1",
    port=3306,
    database="tubestst",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

views = Blueprint('views', __name__)
mysql = MySQL(views)
cur = conn.cursor()
views.config['SECRET_TOKEN'] = 'aduhAPIpanas'


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route("/ecommerce", methods = ['GET'])
def ecommerce():
    return render_template("ecommerce.html")

@views.route("/ecommerce/getall", methods = ['GET'])
def ecommerce():
    cur.execute("SELECT * FROM ecommerce")
    rv = cur.fetchall()  
    return jsonify(rv)

@views.route("/uscovid", methods = ['GET'])
def uscovid():
    return render_template("uscovid.html")

@views.route("/uscovid/getall", methods = ['GET'])
def uscovid():
    cur.execute("SELECT * FROM uscovid")
    rv = cur.fetchall()  
    return jsonify(rv)

@views.route("/uscovid/insert", methods=['POST'])
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

@views.route("/uscovid/update", methods = ['PUT'])
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

@views.route('/uscovid/delete', methods=['DELETE'])
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

@views.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response  

@views.route("/ecommerce/insert", methods=['POST'])
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

@views.route("/ecommerce/update", methods = ['PUT'])
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

@views.route('/ecommerce/delete', methods=['DELETE'])
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

