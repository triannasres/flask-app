from flask import Flask, request
from werkzeug.security import check_password_hash, generate_password_hash
import simplejson
import datetime
import pymysql
import jwt

app = Flask(__name__)
app.config['SECRET_TOKEN'] = 'yzyqhAd_VUWggLsz-Lg6kg'

conn = pymysql.connect(
    user="root",
    password="",
    host="127.0.0.1",
    port=3306,
    database="tubestst",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

cur = conn.cursor()

def validate_token():
    auth = request.headers.get('Authorization')

    if not auth:
        raise Exception('No auth provided')

    token = auth.split()[1]

    data = jwt.decode(token, app.config['SECRET_TOKEN'], ['HS256'])

    cur.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
    user = cur.fetchone()
    if cur.rowcount > 0:
        if user['pass_hash'] != data['pass_hash']:
            raise Exception('Password incorrect')
    else:
        raise Exception('No user found')

    return data

@app.route('/')
def home():
    try:
        validate_token()
    except Exception as e:
        return e.args[0],401
    cur.execute('SELECT * FROM imdb_topgrossing ORDER BY movies_id')
    data = cur.fetchall()
    return simplejson.dumps(data)

@app.route('/add_movie', methods=['POST'])
def add_movie():
    try:
        validate_token()
    except Exception as e:
        return e.args[0],401
    cur.execute("""
    INSERT INTO imdb_topgrossing (
        Title, Movie_Info, Distributor,
        Release_Date, Domestic_Sales_In_, 
        International_Sales_in_, World_Sales_in_,
        Genre, Certificate, Runtime, IMDB_Rating, Meta_score,
        Director, Gross
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s
    )
    """, (
        request.args.get('Title'),
        request.args.get('Movie_Info'),
        request.args.get('Distributor'),
        request.args.get('Release_Date'),
        request.args.get('Domestic_Sales_in_', type=int),
        request.args.get('International_Sales_in_', type=int),
        request.args.get('World_Sales_in_', type=int),
        str(request.args.getlist('Genre')),
        request.args.get('Certificate'),
        request.args.get('Runtime'),
        request.args.get('IMDB_Rating', type=float),
        request.args.get('Meta_score'),
        request.args.get('Director'),
        request.args.get('Gross')
    ))

    return "Success"

@app.route('/get_movie_title')
def get_movie_title():
    try:
        validate_token()
    except Exception as e:
        return e.args[0],401
    cur.execute("SELECT * FROM imdb_topgrossing WHERE LOWER(Title) LIKE CONCAT(%s, '%%')", (request.args.get('Title').lower(),))
    return simplejson.dumps(cur.fetchall())

@app.route('/get_movie_id')
def get_movie_id():
    try:
        validate_token()
    except Exception as e:
        return e.args[0],401
    movies_id = request.args.get('movies_id', type=int)
    cur.execute('SELECT * FROM imdb_topgrossing WHERE movies_id = %s', (movies_id,))
    return simplejson.dumps(cur.fetchone())

@app.route('/delete_movie', methods=['DELETE'])
def delete_movie():
    try:
        validate_token()
    except Exception as e:
        return e.args[0],401
    movies_id = request.args.get('movies_id', type=int)
    cur.execute('DELETE FROM imdb_topgrossing WHERE movies_id = %s', (movies_id,))
    return "Success"

@app.route('/update_movie', methods=['PUT'])
def update_movie():
    try:
        validate_token()
    except Exception as e:
        return e.args[0],401
    movies_id = request.args.get('movies_id', type=int)

    cur.execute('SELECT * FROM imdb_topgrossing WHERE movies_id = %s', (movies_id,))
    current = cur.fetchone()

    cur.execute("""
    UPDATE imdb_topgrossing SET
        Title = %s,
        Movie_Info = %s,
        Distributor = %s,
        Release_Date = %s,
        Domestic_Sales_In_ = %s,
        International_Sales_in_ = %s,
        World_Sales_in_ = %s,
        Genre = %s,
        Certificate = %s,
        Runtime = %s,
        IMDB_Rating = %s,
        Meta_score = %s,
        Director = %s,
        Gross = %s
    WHERE movies_id = %s
    """, (
        request.args.get('Title', current.get('Title')),
        request.args.get('Movie_Info', current.get('Movie_Info')),
        request.args.get('Distributor', current.get('Distributor')),
        request.args.get('Release_Date', current.get('Release_Date')),
        request.args.get('Domestic_Sales_in_', current.get('Domestic_Sales_in_'), int),
        request.args.get('International_Sales_in_', current.get('International_Sales_in_'), int),
        request.args.get('World_Sales_in_', current.get('World_Sales_in_'), int), 
        str(request.args.getlist('Genre')) if request.args.getlist('Genre') else current.get('Genre'),
        request.args.get('Certificate', current.get('Certificate')), 
        request.args.get('Runtime', current.get('Runtime')), 
        request.args.get('IMDB_Rating', current.get('IMDB_Rating'), float),
        request.args.get('Meta_score', current.get('Meta_score')),
        request.args.get('Director', current.get('Director')), 
        request.args.get('Gross', current.get('Gross')),
        movies_id
    ))

    return "Success"

@app.route('/register')
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return "Please provide username and password"

    pass_hash = generate_password_hash(password)

    cur.execute('SELECT * FROM users WHERE username = %s', (username,))

    if cur.rowcount > 0:
        return "Username already exist"
    
    # token = jwt.encode({
    #     'username': username,
    #     'pass_hash': pass_hash
    # }, app.config['SECRET_TOKEN']
    # )

    cur.execute('INSERT INTO users (username, pass_hash) VALUES (%s, %s)', (username, pass_hash))
    return "Register successful, please login to get jwt token"

@app.route('/login')
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return "Please provide username and password"

    cur.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cur.fetchone()

    if cur.rowcount > 0:
        if check_password_hash(user['pass_hash'], password):

            pass_hash = user['pass_hash']
            token = jwt.encode({
                'username': username,
                'pass_hash': pass_hash,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, app.config['SECRET_TOKEN']
            )
            # cur.execute('UPDATE users SET jwt_token = %s', (token,))
            return token
        else:
            return "Incorrect password"
    else:
        return "User not found"