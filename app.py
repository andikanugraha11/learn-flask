from flask import Flask, render_template
from flaskext.mysql import MySQL
from data import Students

app = Flask(__name__)

Students = Students()

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'learn-flask'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


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

if __name__ == '__main__':
    app.run(debug=True)