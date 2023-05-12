from flask import Flask, flash, url_for, redirect, render_template, request, session, jsonify, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, parse_tuple
import mysql.connector
from mysql.connector import Error
from forms import RegistrationForm, LoginForm, AdvertisementForm



app = Flask(__name__)

# DELETE THIS BEFORE DEPLOYMENT !!!!!
app.config['DEBUG'] = True

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure session to use filesystem (instead of signed cookies)

#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)


# Make the WSGI interface available at the top level so wfastcgi can get it.
#wsgi_app = app.wsgi_app


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Connect to MySQL
try:
    db = mysql.connector.connect(host='localhost',
                                         database='zastepca',
                                         user='admin',
                                         password='niepamietam100%')

    if db.is_connected():
        db_Info = db.get_server_info()
        print("Connected to MySQL Server version ", db_Info)

except Error as e:
    print("Error while connecting to MySQL", e)


cursor = db.cursor()
cursor = db.cursor(prepared=True)
cursor = db.cursor(buffered=True)


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]



@app.route("/")
@app.route("/home")
@login_required
def home():
    userId = session["user_id"]
    return render_template('home.html', posts=posts)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        print(form.username.data)
        try:
            # Insert new user to DB
            # Ensure username does not exist
            sql = """ SELECT * FROM users WHERE username = %s """
            values = (form.username.data,)
            cursor.execute(sql, values)
            rows = cursor.rowcount
            if rows != 0:
                flash('Ta nazwa użytkownika jest zajęta', 'danger')
                return render_template('register.html', title='Register', form=form)
            else:
                # Add user to database
                username = form.username.data
                now = datetime.now()
                hash = generate_password_hash(username, method='pbkdf2:sha256', salt_length=8)
                sql = """ INSERT INTO users (username, created_at, hash, last_active) VALUES (%s,%s,%s,%s) """
                values = (username, now, hash, now)
                cursor.execute(sql, values)
                db.commit()

                # Add user personal details to database
                sql =  """ SELECT (id) FROM users WHERE username = %s """
                values = (form.username.data,)
                cursor.execute(sql, values)

                # Get new user id
                rows = cursor.fetchone()
                user_id = rows[0]

                sql = """ INSERT INTO private_users (name, lastname, email, phone_number, user_id) VALUES (%s,%s,%s,%s,%s) """
                values = (form.name.data, form.lastname.data, form.email.data, form.phonenumber.data, user_id)
                cursor.execute(sql, values)

                # Add user profession details to database
                sql = """ INSERT INTO lawyers (profession, region, town, user_id) VALUES (%s,%s,%s,%s) """
                values = (form.profession.data, form.region.data, form.town.data, user_id)
                cursor.execute(sql, values)
                db.commit()

                flash('Poprawnie zarejstrowano, możesz się zalogować', 'info')
                return redirect(url_for('login'))

        # Check if DB operation was succesfull
        except mysql.connector.Error as error:
            print("Failed operation MySQL table {}".format(error))
            flash('Konto nie zostało utworzone z powodu błędu', 'error')
            return render_template('register.html', title='Register', form=form)

    return render_template('register.html', title='Register', form=form)



@app.route("/about")
def about():
    return render_template('about.html', title='About')



@app.route("/advertisements")
@login_required
def advertisements():
    userId = session["user_id"]
    return render_template('advertisements.html', posts=posts)




@app.route("/new-advertisement", methods=['GET', 'POST'])
@login_required
def new_advertisement():


    # https://nagasudhir.blogspot.com/2022/07/forms-in-flask-with-wtforms.html


    # https://tutorial101.blogspot.com/2020/04/python-flask-dynamic-select-box-using.html
    # https://www.youtube.com/watch?v=75djbw0WGEM&t=538s


    # https://stackoverflow.com/questions/41232105/populate-wtforms-select-field-using-value-selected-from-previous-field/41246506#41246506

    form = AdvertisementForm(form_name='AdvertisementForm')

    sql = """ SELECT id, town FROM appeals """
    cursor.execute(sql)
    rows = cursor.fetchall()
    # print(rows)

    form.appeal.choices = [(row[0], row[1]) for row in rows]
    form.court_of_appeal.choices = []
    form.district_court.choices = []
    form.district_court_department.choices = []
    form.regional_court_department.choices = []

    if request.method == 'GET':
        return render_template('new-advertisement.html', form=form)
       

    if form.validate_on_submit() and request.form['form_name'] == 'AdvertisementForm':
       # code to process form
       print('/TODO')
       

    return redirect(url_for('new-advertisement'))
 



# This route is is required for populating AdvertisementForm
@app.route('/_get_court_of_appeal')
def _get_court_of_appeal():

    appeal = request.args.get('appeal', '01', type=str)
    # print(tuple(appeal))
    value = parse_tuple("('%s',)" % appeal)


    sql = """ SELECT id, court_of_appeal FROM appeals WHERE id = %s """
    cursor.execute(sql, value)
    rows = cursor.fetchall()
    # print(rows)

    court_of_appeal = [(row[0], row[1]) for row in rows]
    # print(court_of_appeal)
    # print(jsonify(court_of_appeal))
    return jsonify(court_of_appeal)


# This route is is required for populating AdvertisementForm
@app.route('/_get_district_court')
def _get_district_court():

    court_of_appeal = request.args.get('court_of_appeal', '01', type=str)
    # print(tuple(court_of_appeal))
    value = parse_tuple("('%s',)" % court_of_appeal)


    sql = """ SELECT id, court FROM district_courts WHERE appeal_id = %s """
    cursor.execute(sql, value)
    rows = cursor.fetchall()
    # print(rows)

    district_court = [(row[0], row[1]) for row in rows]
    # print(district_court)
    # print(jsonify(district_court))
    return jsonify(district_court)



# This route is is required for populating AdvertisementForm
@app.route('/_get_district_court_department')
def _get_district_court_department():

    district_court = request.args.get('district_court', '01', type=str)
    print(tuple(district_court))
    value = parse_tuple("('%s',)" % district_court)


    sql = """ SELECT id, department FROM district_court_departments WHERE district_court_id = %s """
    cursor.execute(sql, value)
    rows = cursor.fetchall()
    print(rows)

    district_court_department = [(row[0], row[1]) for row in rows]
    print(district_court_department)
    print(jsonify(district_court_department))
    return jsonify(district_court_department)



# This route is is required for populating AdvertisementForm
@app.route('/_get_regional_court_department')
def _get_regional_court_department():

    district_court_department = request.args.get('district_court_department', '01', type=str)
    print(tuple(district_court_department))
    value = parse_tuple("('%s',)" % district_court_department)


    sql = """ SELECT id, department FROM regional_courts WHERE district_court_departm_id = %s """
    cursor.execute(sql, value)
    rows = cursor.fetchall()
    print(rows)

    regional_court_department = [(row[0], row[1]) for row in rows]
    print(regional_court_department)
    print(jsonify(regional_court_department))
    return jsonify(regional_court_department)



@app.route("/login", methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        # Forget any user_id
        session.clear()
        print(form.username.data)
        try:
            # Ensure username exists and password is correct
            # Query database for username
            sql = """ SELECT id, username, hash FROM users WHERE username = %s """
            values = (form.username.data,)
            cursor.execute(sql, values)
            rows = cursor.fetchone() # fetchone returns dict, fetchall() returns list
            if cursor.rowcount != 1 or not check_password_hash(rows[2], form.password.data):
                flash('Niepoprawny login lub hasło!', 'error')
                return render_template('login.html', title='Login', form=form)
            else:
                # Remember which user has logged in
                session["user_id"] = rows[0]
                flash('Jesteś zalogowany', 'success')
                return redirect(url_for('home'))

        # Check if DB operation was succesfull
        except mysql.connector.Error as error:
            print("Failed operation MySQL table {}".format(error))
            flash('Wystąpił błąd podczas logowania, spróbuj ponownie', 'error')
            return render_template('login.html', title='Login', form=form)

    return render_template('login.html', title='Login', form=form)



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")














if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    
    app.run(HOST, PORT)