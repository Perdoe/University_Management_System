import pandas as pd
from models.models import db, User, Student, StudentCourse
from flask import Flask
from config.config import Config
import secrets
import string


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def generate_temporary_password():
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(10))


def create_student_accounts(excel_file):
    app = create_app()

    with app.app_context():
        print("Creating student accounts...")
        # Read student data
        students_df = pd.read_excel(excel_file, sheet_name='Students')

        # Keep track of created accounts for reporting
        created_accounts = []
        skipped_accounts = []

        for _, row in students_df.iterrows():
            student_id = row['StudentID']
            # Format username as S + student ID if it's not already in that format
            username = f"S{student_id}" if not student_id.startswith('S') else student_id

            # Check if user account already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                skipped_accounts.append(username)
                continue

            # Generate email (you might want to modify this based on your university's email format)
            email = f"{username}@university.edu"

            # Generate temporary password
            temp_password = generate_temporary_password()

            try:
                # Create User account
                new_user = User(
                    username=username,
                    email=email,
                    user_type='student'
                )
                new_user.set_password(temp_password)
                db.session.add(new_user)

                # Create or update Student record
                student = Student.query.filter_by(student_id=student_id).first()
                if not student:
                    student = Student(
                        student_id=student_id,
                        gender=row['Gender'],
                        major=row['Major']
                    )
                    db.session.add(student)

                db.session.commit()

                created_accounts.append({
                    'username': username,
                    'temp_password': temp_password,
                    'email': email
                })

                print(f"Created account for student {username}")

            except Exception as e:
                print(f"Error creating account for student {username}: {str(e)}")
                db.session.rollback()

        # Generate report of created accounts
        if created_accounts:
            report_df = pd.DataFrame(created_accounts)
            report_df.to_excel('student_account_credentials.xlsx', index=False)
            print("\nTemporary credentials have been saved to 'student_account_credentials.xlsx'")

        print("\nAccount creation summary:")
        print(f"Created: {len(created_accounts)} accounts")
        print(f"Skipped: {len(skipped_accounts)} existing accounts")


def verify_student_data_linkage():
    """Verify that all students have proper data linkage"""
    app = create_app()

    with app.app_context():
        all_students = Student.query.all()
        for student in Student.query.all():
            # Check User account
            username = f"S{student.student_id}" if not student.student_id.startswith('S') else student.student_id
            user = User.query.filter_by(username=username).first()

            # Check courses
            courses = StudentCourse.query.filter_by(student_id=student.student_id).all()

            print(f"\nStudent {student.student_id}:")
            print(f"User account: {'Found' if user else 'Missing'}")
            print(f"Number of courses: {len(courses)}")


if __name__ == '__main__':
    excel_file = 'StudentsCourses.xlsx'  # Your data file

    print("What would you like to do?")
    print("1. Create student accounts from data file")
    print("2. Verify student data linkage")
    choice = input("Enter your choice (1-2): ")

    if choice == '1':
        create_student_accounts(excel_file)
    elif choice == '2':
        verify_student_data_linkage()
    else:
        print("Invalid choice!")