from flask import Flask, flash, url_for, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required
import mysql.connector
from mysql.connector import Error
from forms import RegistrationForm, LoginForm



app = Flask(__name__)

# DELETE THIS BEFORE DEPLOYMENT !!!!!
app.config['DEBUG'] = True

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


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
def home():
    return render_template('home.html', posts=posts)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    print(form.username.data)

    if form.validate_on_submit():

        # Insert new user to DB
        # Ensure username does not exist
        sql = """ SELECT * FROM users WHERE username = %s """
        values = (form.username.data,)
        cursor.execute(sql, values)
        db.commit()
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
            # Check if DB operation was succesfull
            if cursor.rowcount != 0:
                flash('Registration succesful! You can log in now', 'info')
                return render_template('login.html', title='Login', form=form)
            else:
                flash('Konto nie zostało utworzone z powodu błędu', 'error')
                return render_template('register.html', title='Register', form=form)

    return render_template('register.html', title='Register', form=form)



@app.route("/about")
def about():
    return render_template('about.html', title='About')



@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)



















if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    
    app.run(HOST, PORT)