import pandas as pd
from models.models import db, User, Teacher, Staff
from flask import Flask
from config.config import Config
import secrets
import string


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(10))


def create_staff_teacher_accounts(excel_file):
    app = create_app()

    with app.app_context():
        # Create teacher accounts
        teachers_df = pd.read_excel(excel_file, sheet_name='Instructors')
        teacher_accounts = []

        for _, row in teachers_df.iterrows():
            instructor_id = row['InstructorID']
            username = f"T{instructor_id}" if not instructor_id.startswith('T') else instructor_id
            email = f"{username}@university.edu"
            temp_password = generate_password()

            if not User.query.filter_by(username=username).first():
                new_user = User(
                    username=username,
                    email=email,
                    user_type='teacher'
                )
                new_user.set_password(temp_password)
                db.session.add(new_user)

                teacher_accounts.append({
                    'username': username,
                    'password': temp_password,
                    'email': email
                })

        # Create staff accounts
        staff_df = pd.read_excel(excel_file, sheet_name='Staffs')
        staff_accounts = []

        for _, row in staff_df.iterrows():
            staff_id = row['StaffID']
            username = f"ST{staff_id}" if not staff_id.startswith('ST') else staff_id
            email = f"{username}@university.edu"
            temp_password = generate_password()

            if not User.query.filter_by(username=username).first():
                new_user = User(
                    username=username,
                    email=email,
                    user_type='staff'
                )
                new_user.set_password(temp_password)
                db.session.add(new_user)

                staff_accounts.append({
                    'username': username,
                    'password': temp_password,
                    'email': email
                })

        try:
            db.session.commit()

            # Save credentials to Excel files
            if teacher_accounts:
                pd.DataFrame(teacher_accounts).to_excel('LOGINS/teacher_credentials.xlsx', index=False)
                print("Teacher credentials saved to 'teacher_credentials.xlsx'")

            if staff_accounts:
                pd.DataFrame(staff_accounts).to_excel('LOGINS/staff_credentials.xlsx', index=False)
                print("Staff credentials saved to 'staff_credentials.xlsx'")

        except Exception as e:
            print(f"Error creating accounts: {str(e)}")
            db.session.rollback()


if __name__ == '__main__':
    excel_file = 'StudentsCourses.xlsx'  # Your data file
    create_staff_teacher_accounts(excel_file)