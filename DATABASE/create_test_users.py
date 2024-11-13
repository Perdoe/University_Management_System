from flask import Flask
from models.models import db, User, Teacher, Student, Staff
from config.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def create_test_users():
    app = create_app()

    with app.app_context():
        # First delete existing test users if they exist
        User.query.filter(User.username.in_(['S12345', 'T12345', 'ST12345'])).delete()
        Student.query.filter(Student.student_id == 'S12345').delete()
        Teacher.query.filter(Teacher.instructor_id == 'T12345').delete()
        Staff.query.filter(Staff.staff_id == 'ST12345').delete()
        db.session.commit()

        # Then create new test users

    with app.app_context():
        # Create a student user
        student_user = User(
            username='S12345',
            email='student@university.edu',
            user_type='student'
        )
        student_user.set_password('student123')
        student = Student(
            student_id='S12345',
            gender='M',
            major='CIS'
        )

        # Create a teacher user
        teacher_user = User(
            username='T12345',
            email='teacher@university.edu',
            user_type='teacher'
        )
        teacher_user.set_password('teacher123')
        teacher = Teacher(
            instructor_id='T12345',
            instructor_phone='555-0101',
            department_id='CIS',
            hired_semester='F2023'
        )

        # Create a staff user
        staff_user = User(
            username='ST12345',
            email='staff@university.edu',
            user_type='staff'
        )
        staff_user.set_password('staff123')
        staff = Staff(
            staff_id='ST12345',
            department_id='CIS',
            phone='555-0102'
        )

        # Add all users and their corresponding role records
        db.session.add(student_user)
        db.session.add(student)
        db.session.add(teacher_user)
        db.session.add(teacher)
        db.session.add(staff_user)
        db.session.add(staff)

        try:
            db.session.commit()
            print("Test users created successfully!")
        except Exception as e:
            print(f"Error creating test users: {str(e)}")
            db.session.rollback()


if __name__ == '__main__':
    create_test_users()