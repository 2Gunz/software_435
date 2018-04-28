from flask import Flask, render_template, flash, request, redirect, url_for, session, logging
from flask_mysqldb import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_sslify import SSLify
import os

# Start flask application
application = Flask(__name__)

# Force https
sslify = SSLify(application)

# Config MySQL local
application.config['SECRET_KEY'] = os.urandom(32).encode('hex')
application.config['MYSQL_HOST'] = 'localhost'
application.config['MYSQL_USER'] = 'root'
application.config['MYSQL_PASSWORD'] = 'Nava435'
application.config['MYSQL_DB'] = 'schedulerapp'
application.config['MYSQL_CURSORCLASS'] = 'DictCursor'
"""
# Config MySQL AWS RDS
application.config['SECRET_KEY'] = os.urandom(24).encode('hex')
application.config['MYSQL_HOST'] = 'aa168k8g4t45xqt.cx1fprjct8eq.us-west-2.rds.amazonaws.com'
application.config['MYSQL_USER'] = 'root'
# [WARNING]: must change database password for final delivery
application.config['MYSQL_PASSWORD'] = 'Nava435!'
application.config['MYSQL_DB'] = 'schedulerapp'
application.config['MYSQL_CURSORCLASS'] = 'DictCursor'
"""
# Initialize MySQL
mysql = MySQL(application)

# Home page template
@application.route('/')
def index():
    return render_template('home.html')

# About page template 
@application.route('/about')
def about():
    return render_template('about.html')

# Class for registration form format
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
        ])
    confirm = PasswordField('Confirm Password')

# Registration form template
@application.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s,%s,%s,%s)", (name, email, username, password))

        # Commit to db
        mysql.connection.commit()

        # Close the connection
        cur.close()

        flash('You are now registered and can login', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login template
@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get login form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@application.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

# Request forms
@application.route('/frequests')
def frequests():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute("SELECT * FROM requests")

    frequests = cur.fetchall()

    if result > 0:
        return render_template('frequests.html', frequests=frequests)
    else:
        error = 'No Request Forms Found'
        return render_template('frequests.html', error=error)
    # Close connection
    cur.close()

# Single Resquest Form
@application.route('/frequest/<string:id>/')
def frequest(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get request form
    result = cur.execute("SELECT * FROM requests WHERE id = %s", [id])

    frequest = cur.fetchone()

    return render_template('frequest.html', frequest=frequest)

# Dashboard
@application.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get requests
    result = cur.execute("SELECT * FROM requests")

    frequests = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', frequests=frequests)
    else:
        error = 'No Request Forms Found'
        return render_template('dashboard.html', error=error)
    # Close connection
    cur.close()

# Request Form Class
class RequestForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=100)])

"""
**** NEED TO IMPLEMENT REQUEST FORM PARAMETERS AND UPDATE TEMPLATE ****
Days off: [date]
By schdule type - [Full time, part time], [Fixed, flexible, mixed]
By age - [Pediatric, Adult, Geriatric, Family]
By specialty - [Emergency, Urgent Care, Primary Care, Obstetrics]
By license - [Physician, Nurse Midwife, Nurse Practitioner]
Preferences: [Days in row, Weekends, Practice Type, Locations]
"""

# Add Request
@application.route('/add_frequest', methods=['GET', 'POST'])
@is_logged_in
def add_frequest():
    form = RequestForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO requests(title) VALUES(%s)", (title, ))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Request Form Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_frequest.html', form=form)


# Edit Request Form
@application.route('/edit_frequest/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_frequest(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get request form by id
    result = cur.execute("SELECT * FROM requests WHERE id = %s", [id])

    frequest = cur.fetchone()
    cur.close()
    # Get form
    form = RequestForm(request.form)

    # Populate request form fields
    form.title.data = frequest['title']

    if request.method == 'POST' and form.validate():
        title = request.form['title']

        # Create Cursor
        cur = mysql.connection.cursor()
        application.logger.info(title)
        # Execute
        cur.execute ("UPDATE requests SET title=%s WHERE id=%s",(title, id))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Request Form Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_frequest.html', form=form)

# Delete Request Form
@application.route('/delete_frequest/<string:id>', methods=['POST'])
@is_logged_in
def delete_frequest(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM requests WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Request Form Deleted', 'success')

    return redirect(url_for('dashboard'))

# Run program (ignored when using AWS EB)
if __name__ == '__main__':
    application.run(debug=True)