from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import with_appcontext

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return f"<User {self.username}>"

# Define Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    grade = db.Column(db.String(10))
    maths = db.Column(db.Integer)
    science = db.Column(db.Integer)
    english = db.Column(db.Integer)
    hindi = db.Column(db.Integer)
    computer = db.Column(db.Integer)
    #contact details
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    def __repr__(self):
        return f"<Student {self.name}>"

# CLI command to create database
@app.cli.command("create_db")
@with_appcontext
def create_db():
    db.create_all()

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')



@app.route('/student_profile/<int:student_id>')
def student_profile(student_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    student = Student.query.get_or_404(student_id)
    return render_template('student_profile.html', student=student)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        grade = request.form['grade']
        maths = int(request.form['maths'])
        science = int(request.form['science'])
        english = int(request.form['english'])
        hindi = int(request.form['hindi'])
        computer = int(request.form['computer'])
        email = request.form['email']
        phone = request.form['phone']
        new_student = Student(name=name, grade=grade, maths=maths, science=science, english=english, hindi=hindi, computer=computer,email=email,phone=phone)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_student.html')


# Add marks route
@app.route('/add_marks/<int:student_id>', methods=['GET', 'POST'])
def add_marks(student_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        maths = int(request.form['maths'])
        science = int(request.form['science'])
        english = int(request.form['english'])
        hindi = int(request.form['hindi'])
        computer = int(request.form['computer'])
        
        student.maths = maths
        student.science = science
        student.english = english
        student.hindi = hindi
        student.computer = computer

        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('add_marks.html', student=student)

# Route to edit student
@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    # Fetch the student from the database
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        # Update the student details
        student.name = request.form['name']
        student.grade = request.form['grade']
        student.maths = int(request.form['maths'])
        student.science = int(request.form['science'])
        student.english = int(request.form['english'])
        student.hindi = int(request.form['hindi'])
        student.computer = int(request.form['computer'])
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_student.html', student=student)

# Route to delete student
@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    # Fetch the student from the database and delete
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('dashboard'))

# Route to print mark sheet
@app.route('/print_marksheet/<int:student_id>')
def print_marksheet(student_id):
    # Fetch the student from the database
    student = Student.query.get_or_404(student_id)
    # Render the mark sheet template
    return render_template('marksheet.html', student=student)

# Route for dashboard
@app.route('/dashboard')
def dashboard():
    # Fetch all students from the database
    students = Student.query.all()
    return render_template('dashboard.html', students=students)

# Route for logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)