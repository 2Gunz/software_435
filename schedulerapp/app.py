from flask import Flask, render_template, flash, request, redirect, url_for, session, logging
from data import Forms
from flask_mysqldb import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

# Start flask app
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Nava435'
app.config['MYSQL_DB'] = 'schedulerapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

#forms = Forms()

# Home page template
@app.route('/')
def index():
	return render_template('home.html')

# About page template 
@app.route('/about')
def about():
	return render_template('about.html')
"""
# Request form template
@app.route('/forms')
def forms():
	return render_template('forms.html', forms = Forms())
"""
# Class for registration form format
""" NEED: add provider type, specialty, and license"""
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
@app.route('/register', methods=['GET', 'POST'])
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
@app.route('/login', methods=['GET', 'POST'])
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
                return redirect(url_for('about'))
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
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))
"""
# Class for request form format
class RequestForm(Form):
    # Enter request form entries here
    # Days off: [date]
    # By schdule type - [Full time, part time], [Fixed, flexible, mixed]
    # By age - [Pediatric, Adult, Geriatric, Family]
    # By specialty - [Emergency, Urgent Care, Primary Care, Obstetrics]
    # By license - [Physician, Nurse Midwife, Nurse Practitioner]
    # Preferences: [Days in row, Weekends, Practice Type, Locations]
"""
# Request form template
@app.route('/requestform', methods=['GET', 'POST'])
def requestform():
    return render_template('requestform.html')
    """
    # Enter request template functionality and validation here
    # Most values will probably be checkboxes
    form = RequestForm(request.form)
    if request.method == 'POST' and form.validate():
        # NEED: add validators for RequestForm class

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, daysinrow, weekends , practice type, location) VALUES(%s,%s,%s,%s)", (name, email, username, password))

        # Commit to db
        mysql.connection.commit()

        # Close the connection
        cur.close()

        flash('Thank you for submitting your schedule request', 'success')

        return redirect(url_for('logout'))
    return render_template('requestform.html', form=form)
    """

# Run program
if __name__ == '__main__':
	app.secret_key='Secret_Nava'
	app.run(debug=True)