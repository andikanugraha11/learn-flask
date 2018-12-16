from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

from data import Students

app = Flask(__name__)

Students = Students()

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'learn_flask'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/student")
def students():
    return render_template('students.html', students= Students)

@app.route("/student/<string:id>")
def student(id):
    return render_template('student.html', id=id)

# Register Form
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=4, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('passConfirm', message='Password do not  match')
    ])
    passConfirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)", (name,email,username,password))

        # commit to DB
        mysql.connection.commit()

        # close connection
        cur.close()

        flash("You're now registered and can login", "success")
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

# login wraps check
def is_login(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'login' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorize, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        # create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0 :
            data = cur.fetchone()
            password = data['password']

            # compare password
            if sha256_crypt.verify(password_candidate, password):
                # pass
                session['login'] = True
                session['username'] = username

                flash("You're now logged in", "success")
                return redirect(url_for('dashboard'))
            else:
                error = 'Wrong Password'
                return render_template('login.html', error=error)
            cur.close()
        else:
             error = 'Username not found'
             return render_template('login.html', error=error)

    return render_template('login.html')

@app.route("/dashboard")
@is_login
def dashboard():
    return render_template('dashboard.html')

@app.route("/logout")
def logout():
    session.clear()
    flash("You're now logged out","success")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.secret_key='secret121'
    app.run(debug=True)