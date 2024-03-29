﻿from flask import Flask, flash, url_for, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date  
from helpers import login_required, parse_tuple, pln
import mysql.connector
from mysql.connector import Error
from forms import RegistrationForm, LoginForm, AdvertisementForm, BidForm



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


# Make the WSGI interface available at the top level so wfastcgi can get it.
#wsgi_app = app.wsgi_app


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["pln"] = pln


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


# Change mysql connector behavior
cursor = db.cursor()
cursor = db.cursor(prepared=True)
cursor = db.cursor(buffered=True)
cursor = db.cursor(dictionary=True)


@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template('home.html')


@app.route("/ajaxlivesearch",methods=["POST","GET"])
@login_required
def ajaxlivesearch():
    if request.method == 'POST':
        search_word = request.form.get('query')
        if (search_word is not None):
            print(search_word)
            try:
                if search_word == '':
                    sql = """ SELECT advertisements.id, title, start_date, salary, location, address, date_of_publication, group_concat(DISTINCT tags.name) AS tags,
                          group_concat(DISTINCT order_types.name) AS order_types FROM advertisements LEFT JOIN tagmap ON advertisements.id=tagmap.advertisement_id LEFT JOIN tags ON tagmap.tag_id=tags.tag_id LEFT JOIN order_type_map ON advertisements.id=order_type_map.advertisement_id LEFT JOIN order_types ON order_type_map.type_id=order_types.type_id GROUP BY advertisements.id """

                    cursor.execute(sql)
                    advertisements = cursor.fetchall()
                else:    
                        sql = """ SELECT advertisements.id, title, start_date, salary, location, address, date_of_publication, group_concat(DISTINCT tags.name) AS tags,
                               group_concat(DISTINCT order_types.name) AS order_types FROM advertisements LEFT JOIN tagmap ON advertisements.id=tagmap.advertisement_id LEFT JOIN tags ON tagmap.tag_id=tags.tag_id LEFT JOIN order_type_map ON advertisements.id=order_type_map.advertisement_id LEFT JOIN order_types ON order_type_map.type_id=order_types.type_id GROUP BY advertisements.id HAVING tags LIKE %s OR title LIKE %s OR location LIKE %s """

                        values = ("%{}%".format(search_word), "%{}%".format(search_word),"%{}%".format(search_word))
                        cursor.execute(sql, values)     
                        advertisements = cursor.fetchall()
                        rows = cursor.rowcount
                        print(rows)
                        print(advertisements)
                return jsonify({'htmlresponse': render_template('response.html', advertisements=advertisements, rows=rows)})

            except mysql.connector.Error as error:
                print("Failed operation MySQL table {}".format(error))
                flash('Błąd połączenia z bazą', 'error')
                return jsonify({'htmlresponse': render_template('response.html', advertisements=advertisements, rows=rows)})

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
            rows = cursor.fetchall()
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

                # Get new user id
                user_id = cursor.lastrowid

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


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    
    try:
        sql = """ SELECT * FROM (SELECT users.id As id, username, town,
              name as proffesion FROM users join lawyers on users.id=lawyers.user_id join professions on lawyers.profession=professions.id)tb WHERE id=%s """
        values = (session["user_id"],)
        cursor.execute(sql, values)
        rows = cursor.fetchall()

        return render_template('profile.html', rows=rows)

    except mysql.connector.Error as error:
        print("Failed operation MySQL table {}".format(error))
        flash('Błąd połączenia z bazą', 'error') 
        return render_template('profile.html', rows=rows)

@app.route("/history", methods=['GET', 'POST'])
@login_required
def history():

    try:
        sql = """ SELECT action, time FROM history WHERE user_id=%s """
        values = (session["user_id"],)
        cursor.execute(sql, values)
        rows = cursor.fetchall()
        print(session["user_id"])
        print(rows)
        return render_template('history.html', rows=rows)

    except mysql.connector.Error as error:
           print("Failed operation MySQL table {}".format(error))
           flash('Błąd połączenia z bazą', 'error') 
           return render_template('history.html', rows=rows)

@app.route("/advertisements")
@login_required
def advertisements():

    try:
        sql = """ SELECT advertisements.id, title, start_date, start_time, duration, salary, location, address, file_review, invoice, description, date_of_publication, username,
              group_concat(tags.name) AS tags FROM advertisements LEFT JOIN tagmap ON advertisements.id=tagmap.advertisement_id LEFT JOIN tags ON tagmap.tag_id=tags.tag_id JOIN users ON advertisements.user_id=users.id GROUP BY advertisements.id """
        cursor.execute(sql)
        advertisements = cursor.fetchall()
        print(advertisements)
        return render_template('advertisements.html', advertisements=advertisements)

    except mysql.connector.Error as error:
           print("Failed operation MySQL table {}".format(error))
           flash('Błąd połączenia z bazą', 'error') 
           return render_template('advertisements.html', advertisements=advertisements)


@app.route("/advertisement-details/<string:id>", methods=['GET', 'POST'])
@login_required
def advertisement_details(id):

    form = BidForm()

    print(id)
    username = session["username"]

    try:
        sql = """ SELECT advertisements.id, title, start_date, start_time, duration, salary, location, address, file_review, invoice, description, date_of_publication, username,
       group_concat(DISTINCT tags.name) AS tags, group_concat(DISTINCT order_types.name) AS order_types FROM advertisements LEFT JOIN tagmap ON advertisements.id=tagmap.advertisement_id LEFT JOIN tags ON tagmap.tag_id=tags.tag_id LEFT JOIN order_type_map ON advertisements.id=order_type_map.advertisement_id LEFT JOIN order_types ON order_type_map.type_id=order_types.type_id JOIN users ON advertisements.user_id=users.id WHERE (advertisements.id = %s) GROUP BY advertisements.id """
        values = (id,)
        cursor.execute(sql, values)
        details = cursor.fetchall()

        sql =  """ SELECT bids.id, date, bid, username FROM bids JOIN users ON bids.bidder_id = users.id WHERE adv_id = %s """
        cursor.execute(sql, values)
        bids = cursor.fetchall()
        
        if (cursor.rowcount == 0):
            return render_template('advertisement-details.html', details=details, username=username, form=form)
        else:
            return render_template('advertisement-details.html', details=details, bids=bids, username=username, form=form)

    except mysql.connector.Error as error:
        print("Failed operation MySQL table {}".format(error))


@app.route("/delete-advertisement/<int:id>", methods=['POST'])
@login_required
def delete_advertisement(id):

    try:
        sql = """ DELETE FROM advertisements WHERE id = %s """
        values = (id,)
        cursor.execute(sql, values)
        db.commit()

        flash('Ogłoszenie usunięte', 'info')
        return redirect(url_for('advertisements'))

    except mysql.connector.Error as error:
        print("Failed operation MySQL table {}".format(error))
        if(str(error.sqlstate)=='23000'):
            flash('Najpierw odrzuć wszystkie oferty', 'error')
        else:
            flash('Ogłoszenie nie zostało usunięte z powodu błędu', 'error')

        return redirect(url_for('advertisements'))


@app.route("/insert-bid", methods=['POST'])
@login_required
def insert_bid():

    form = BidForm()

    bid = form.bid.data
    adv_id = form.adv_id.data
    print(bid)
    print(adv_id)

    try:
        sql = """ INSERT INTO bids (adv_id, bidder_id, bid, date, status) VALUES (%s,%s,%s,%s,%s) """
        values = (adv_id, session["user_id"], bid, date.today().isoformat(), 'ACTIVE')
        cursor.execute(sql, values)
        db.commit()

        # Add entry to user history table
        sql = """ INSERT INTO history (action, time, user_id) VALUES (%s, %s, %s) """
        values = ('Wysłałeś ofertę do ogłoszenia', datetime.now(), session["user_id"])
        cursor.execute(sql, values)
        db.commit()

        flash('Oferta została wysłana', 'info')
        return redirect(url_for('advertisements'))

    except mysql.connector.Error as error:
        print("Failed operation MySQL table {}".format(error))

        flash('Oferta nie została wysłana z powodu błędu', 'error')
        return redirect(url_for('advertisements'))


@app.route("/new-advertisement", methods=['GET', 'POST'])
@login_required
def new_advertisement():

    userId = session["user_id"]

    form = AdvertisementForm(form_name='AdvertisementForm')

    # Fill dropdowns with all possible choices otherwise wtforms validation will fail
    try:
        sql = """ SELECT id, town FROM appeals """
        cursor.execute(sql)
        rows = cursor.fetchall()

        form.appeal.choices = [(0, "---")]+[(row['id'], row['town']) for row in rows]

        sql = """ SELECT id, court_of_appeal FROM appeals """
        cursor.execute(sql)
        rows = cursor.fetchall()
        print(rows)

        form.court_of_appeal.choices = [(0, "---")]+[(row['id'], row['court_of_appeal']) for row in rows]

        sql = """ SELECT id, court FROM district_courts """
        cursor.execute(sql)
        rows = cursor.fetchall()

        form.district_court.choices = [(0, "---")]+[(row['id'], row['court']) for row in rows]

        sql = """ SELECT id, department FROM district_court_departments """
        cursor.execute(sql)
        rows = cursor.fetchall()

        form.district_court_department.choices = [(0, "---")]+[(row['id'], row['department']) for row in rows]
    
        sql = """ SELECT id, department FROM regional_courts """
        cursor.execute(sql)
        rows = cursor.fetchall()

        form.regional_court_department.choices = [(0, "---")]+[(row['id'], row['department']) for row in rows]
    
    except mysql.connector.Error as error:
        print("Failed operation MySQL table {}".format(error))
        flash('Błąd połączenia z bazą', 'error')

    if form.validate_on_submit(): 

       # Get choosen location
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
            choosen_court = key
       
       for field in form:
           if field.name == choosen_court:
               print(dict(field.choices).get(field.data))
               location = dict(field.choices).get(field.data)
       
       appeal = None                            
       court_of_appeal = None                   
       district_court = None                    
       district_court_department = None         
       regional_court_department = None         

       # Get choosen appeal
       if form.appeal.data != None:
           if form.appeal.data != 0:
               appeal = form.appeal.data

       # Get choosen court_of appeal
       if form.court_of_appeal.data != None:
           if form.court_of_appeal.data != 0:
               court_of_appeal = form.court_of_appeal.data

       # Get choosen district court
       if form.district_court.data != None:
           if form.district_court.data != 0:
               district_court = form.district_court.data

       # Get choosen district court department
       if form.district_court_department.data != None:
           if form.district_court_department.data != 0:
               district_court_department = form.district_court_department.data

       # Get choosen regional court department
       if form.regional_court_department.data != None:
           if form.regional_court_department.data != 0:
               regional_court_department = form.regional_court_department.data
        
       # Insert advertisement data to database
       try:  

           sql = """ INSERT INTO advertisements (title, start_date, start_time, duration, salary,
                 location, address, file_review, invoice, description, date_of_publication, status,
                 user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """

           values = (form.title.data, form.start_date.data, form.start_time.data, form.duration.data, form.salary.data,
                    location, form.address.data, form.file_review.data, form.invoice.data, form.description.data,
                    datetime.now(), 'ACTIVE', userId)

           cursor.execute(sql, values)
           db.commit()
           
           # Get new advertisment id
           advertisement_id = cursor.lastrowid

           # Insert advertisement location details data to database
           sql = """ INSERT advertisements_courts (appeal, court_of_appeal, district_court, district_court_department, regional_court_department,
                 advertisement_id) values (%s,%s,%s,%s,%s,%s) """
           values = (appeal, court_of_appeal, district_court, district_court_department, regional_court_department, advertisement_id)
           cursor.execute(sql, values)
           db.commit()

           # Add tags to database (Toxi solution)
           tags = request.form.getlist('tags')
           # Check if user added any tag
           if (tags != ['']):
               print(tags)
               for tag in tags:
                   print(tag)
                   # Prevent inserting duplicated tags
                   sql = """ INSERT INTO tags (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=name """
                   value = parse_tuple("('%s',)" % tag)
                   cursor.execute(sql, value)
                   db.commit()

                   # Get new tag id
                   tag_id = None
                   tag_id = cursor.lastrowid
                   print(tag_id)
               
                   if (tag_id == 0): # 23000 error handler (when tag already exist)
                       print('if sie odpala')
                       sql = """ SELECT tag_id FROM tags WHERE name = %s """
                       cursor.execute(sql, value)
                       rows = cursor.fetchone()
                       tag_id = rows['tag_id']
            
                   sql = """ INSERT INTO tagmap (advertisement_id, tag_id) VALUES (%s, %s) """
                   values = (advertisement_id, tag_id)
                   cursor.execute(sql, values)
                   db.commit()

           # Add order types to DB - array table solution
           order_types = form.order_type.data
           # Check if user selected any type
           if (order_types != ['']):
               print(order_types)
               for order_type in order_types:
                   print(order_type)

                   sql = """ INSERT INTO order_type_map (advertisement_id, type_id) VALUES (%s, %s) """
                   values = (advertisement_id, order_type)
                   cursor.execute(sql, values)
                   db.commit()

            # Add entry to user history table
                   sql = """ INSERT INTO history (action, time, user_id) VALUES (%s, %s, %s) """
                   values = ('Utworzyłeś nowe ogłoszenie', datetime.now(), userId)
                   cursor.execute(sql, values)
                   db.commit()


           flash('Ogłoszenie dodane', 'info')
           return redirect(url_for('advertisements'))

       # Check if DB operation was succesfull
       except mysql.connector.Error as error:
           print("Failed operation MySQL table {}".format(error))
           flash('Ogłoszenie nie zostało dodane z powodu błędu', 'error')
           return render_template('new-advertisement.html', form=form)


    return render_template('new-advertisement.html', form=form)
 

# This route is required for populating AdvertisementForm
@app.route('/_get_court_of_appeal')
def _get_court_of_appeal():

    appeal = request.args.get('appeal', '01', type=str)
    print(tuple(appeal))
    value = parse_tuple("('%s',)" % appeal)

    try:
        sql = """ SELECT id, court_of_appeal FROM appeals WHERE id = %s """
        cursor.execute(sql, value)
        rows = cursor.fetchall()
        court_of_appeal = [(0, "---")]+[(row['id'], row['court_of_appeal']) for row in rows]
        print(court_of_appeal)
        print(jsonify(court_of_appeal))
        return jsonify(court_of_appeal)

    except mysql.connector.Error as error:
        print("Failed operation MySQL table {}".format(error))
        flash('Błąd połączenia z bazą danych', 'error')
        return jsonify(court_of_appeal)

# This route is required for populating AdvertisementForm
@app.route('/_get_district_court')
def _get_district_court():

    court_of_appeal = request.args.get('court_of_appeal', '01', type=str)
    value = parse_tuple("('%s',)" % court_of_appeal)

    try:
        sql = """ SELECT id, court FROM district_courts WHERE appeal_id = %s """
        cursor.execute(sql, value)
        rows = cursor.fetchall()
        district_court = [(0, "---")]+[(row['id'], row['court']) for row in rows]
        return jsonify(district_court)

    except mysql.connector.Error as error:
        print("Failed operation MySQL table {}".format(error))
        flash('Błąd połączenia z bazą danych', 'error')
        return jsonify(district_court)

# This route is required for populating AdvertisementForm
@app.route('/_get_district_court_department')
def _get_district_court_department():

    try:
        district_court = request.args.get('district_court', '01', type=str)
        print(tuple(district_court))
        value = parse_tuple("('%s',)" % district_court)


        sql = """ SELECT id, department FROM district_court_departments WHERE district_court_id = %s """
        cursor.execute(sql, value)
        rows = cursor.fetchall()
        print(rows)

        district_court_department = [(0, "---")]+[(row['id'], row['department']) for row in rows]
        print(district_court_department)
        print(jsonify(district_court_department))
        return jsonify(district_court_department)

    except mysql.connector.Error as error:
        print("Failed operation MySQL table {}".format(error))
        flash('Błąd połączenia z bazą danych', 'error')
        return jsonify(district_court_department)

# This route is is required for populating AdvertisementForm
@app.route('/_get_regional_court_department')
def _get_regional_court_department():

    try:
        district_court_department = request.args.get('district_court_department', '01', type=str)
        print(tuple(district_court_department))
        value = parse_tuple("('%s',)" % district_court_department)
        sql = """ SELECT id, department FROM regional_courts WHERE district_court_departm_id = %s """
        cursor.execute(sql, value)
        rows = cursor.fetchall()
        print(rows)
        regional_court_department = [(0, "---")]+[(row['id'], row['department']) for row in rows]
        print(regional_court_department)
        print(jsonify(regional_court_department))
        return jsonify(regional_court_department)

    except mysql.connector.Error as error:
        print("Failed operation MySQL table {}".format(error))
        flash('Błąd połączenia z bazą danych', 'error')
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
            if cursor.rowcount != 1 or not check_password_hash(rows['hash'], form.password.data):
                flash('Niepoprawny login lub hasło!', 'error')
                return render_template('login.html', title='Login', form=form)
            else:
                # Remember which user has logged in
                session["user_id"] = rows['id']
                session["username"] = rows['username']
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