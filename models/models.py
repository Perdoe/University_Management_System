from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.String(10), unique=True)
    instructor_phone = db.Column(db.String(20))
    department_id = db.Column(db.String(10))
    hired_semester = db.Column(db.String(10))

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(10), unique=True)
    gender = db.Column(db.String(1))
    major = db.Column(db.String(10))

class Staff(db.Model):
    __tablename__ = 'staffs'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(10), unique=True)
    department_id = db.Column(db.String(10))
    phone = db.Column(db.String(20))

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.String(10), unique=True)
    building = db.Column(db.String(10))
    office = db.Column(db.String(20))
    major_offered = db.Column(db.Text)
    total_hours_req = db.Column(db.String(10))
    advisor_id = db.Column(db.String(10))
    advisor_phone = db.Column(db.String(20))

class InstructorCourse(db.Model):
    __tablename__ = 'instructor_courses'
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.String(10))
    course_prefix = db.Column(db.String(10))
    course_number = db.Column(db.String(10))
    credits = db.Column(db.String(5))  # Changed from Integer to String
    semester = db.Column(db.String(5))
    year_taught = db.Column(db.String(10))

class StudentCourse(db.Model):
    __tablename__ = 'student_courses'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(10))          # U1, U3, etc.
    course_prefix = db.Column(db.String(10))       # CIS, EGN, CNT, etc.
    course_number = db.Column(db.String(10))       # 2233, 3420, etc.
    semester = db.Column(db.String(5))             # F, S, U
    year_taken = db.Column(db.String(10))          # 2019, 2020, etc.
    grade = db.Column(db.String(2))                # A, B, C, D, F