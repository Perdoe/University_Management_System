from flask import Flask
from models.models import db, User, Student
from config.config import Config


def verify_accounts():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Check all users in the database
        all_users = User.query.all()
        print("\nUser Accounts in Database:")
        print("-" * 50)
        for user in all_users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"User Type: {user.user_type}")
            # Check if there's a corresponding student record
            if user.user_type == 'student':
                student = Student.query.filter_by(
                    student_id=user.username.replace('S', '') if user.username.startswith('S') else user.username
                ).first()
                print(f"Linked Student Record: {'Yes' if student else 'No'}")
            print("-" * 50)


if __name__ == '__main__':
    verify_accounts()