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

    # https://stackoverflow.com/questions/41232105/populate-wtforms-select-field-using-value-selected-from-previous-field/41246506#41246506

    userId = session["user_id"]

    form = AdvertisementForm(form_name='AdvertisementForm')

    # fill dropdowns with all possible choices otherwise wtforms validation will fail

    sql = """ SELECT id, town FROM appeals """
    cursor.execute(sql)
    rows = cursor.fetchall()

    form.appeal.choices = [(0, "---")]+[(row[0], row[1]) for row in rows]

    sql = """ SELECT id, court_of_appeal FROM appeals """
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(rows)

    form.court_of_appeal.choices = [(0, "---")]+[(row[0], row[1]) for row in rows]

    sql = """ SELECT id, court FROM district_courts """
    cursor.execute(sql)
    rows = cursor.fetchall()

    form.district_court.choices = [(0, "---")]+[(row[0], row[1]) for row in rows]

    sql = """ SELECT id, department FROM district_court_departments """
    cursor.execute(sql)
    rows = cursor.fetchall()

    form.district_court_department.choices = [(0, "---")]+[(row[0], row[1]) for row in rows]
    
    sql = """ SELECT id, department FROM regional_courts """
    cursor.execute(sql)
    rows = cursor.fetchall()

    form.regional_court_department.choices = [(0, "---")]+[(row[0], row[1]) for row in rows]
       

    if form.validate_on_submit(): 
       #and request.form['form_name'] == 'AdvertisementForm':
       # code to process form

       # get choosen location
       location = ''
       courtsData = {}
       choosen_court = ''

       keys_to_add = [form.appeal.name, form.court_of_appeal.name, form.district_court.name,
                     form.district_court_department.name, form.regional_court_department.name] 
       vals_to_add = [form.appeal.data, form.court_of_appeal.data, form.district_court.data,
                     form.district_court_department.data, form.regional_court_department.data]
       
       for key, val in zip(keys_to_add, vals_to_add): 
           courtsData[key] = val 

       for key, value in courtsData.items():
           if value is None:
            continue
           if value > 0:
            # print(key)
            # print(value)
            choosen_court = key
       
       for field in form:
           if field.name == choosen_court:
               print(dict(field.choices).get(field.data))
               location = dict(field.choices).get(field.data)  # VARCHAR(120) NOT NULL sprawdzić w bazie jak max długi 
       
       appeal = None                            # INT(1) NULL
       court_of_appeal = None                   # INT(1) NULL
       district_court = None                    # INT(2) NULL
       district_court_department = None         # INT(2) NULL
       regional_court_department = None         # INT(2) NULL

       # get choosen appeal
       if form.appeal.data != None:
           if form.appeal.data != 0:
               appeal = form.appeal.data

       # get choosen court_of appeal
       if form.court_of_appeal.data != None:
           if form.court_of_appeal.data != 0:
               court_of_appeal = form.court_of_appeal.data

       # get choosen district court
       if form.district_court.data != None:
           if form.district_court.data != 0:
               district_court = form.district_court.data

       # get choosen district court department
       if form.district_court_department.data != None:
           if form.district_court_department.data != 0:
               district_court_department = form.district_court_department.data

       # get choosen regional court department
       if form.regional_court_department.data != None:
           if form.regional_court_department.data != 0:
               regional_court_department = form.regional_court_department.data
        
       
       skills = request.form.getlist('tags')
       for value in skills:  
            print([value])
            # cur.execute("INSERT INTO tags (skillname) VALUES (%s)",[value])
            # conn.commit() 
       
       print(form.title.data)                               # VARCHAR(50) NOT NULL
       print(form.start_date.data)                          # DATE NOT NULL
       print(form.start_time.data)                          # TIME NOT NULL
       print(form.duration.data)                            # INT(2) NOT NULL
       print(form.salary.data)                              # DECIMAL(10, 2) NULL
       print(form.address.data)                             # VARCHAR(150) NOT NULL
       print(form.order_type.data)                          # JSON NOT NULL
       print(form.file_review.data)                         # BOOLEAN NOT NULL
       print(form.description.data)                         # VARCHAR(255) NOT NULL
       print(json.dumps(request.form.getlist('tags')))      # JSON NULL
       print(userId)                                        # VARCHAR(50) NOT NULL

       # insert advertisement data to database
       try:
           sql = """ INSERT INTO advertisements (title, start_date, start_time, duration, salary,
                location, address, order_type, file_review, description, tags, date_of_publication,
                user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """

           values = (form.title.data, form.start_date.data, form.start_time.data, form.duration.data, form.salary.data,
                    location, form.address.data, json.dumps(form.order_type.data), form.file_review.data, form.description.data,
                    json.dumps(request.form.getlist('tags')), datetime.now(), userId)

           cursor.execute(sql, values)
           db.commit()


           # Get new advertisment id
           # rows = cursor.fetchone()
           # advertisement_id = rows[0]



           flash('Ogłoszenie dodane', 'info')
           return redirect(url_for('advertisements'))

       # Check if DB operation was succesfull
       except mysql.connector.Error as error:
           print("Failed operation MySQL table {}".format(error))
           flash('Ogłoszenie nie zostało dodane z powodu błędu', 'error')
           return render_template('new-advertisement.html', form=form)


    return render_template('new-advertisement.html', form=form)
 



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

    court_of_appeal = [(0, "---")]+[(row[0], row[1]) for row in rows]
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

    district_court = [(0, "---")]+[(row[0], row[1]) for row in rows]
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

    district_court_department = [(0, "---")]+[(row[0], row[1]) for row in rows]
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

    regional_court_department = [(0, "---")]+[(row[0], row[1]) for row in rows]
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