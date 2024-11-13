from flask import Flask
from models.models import db, StudentCourse
from config.config import Config


def cleanup_database():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        try:
            # Delete all records from student_courses table
            print("Deleting all student course records...")
            StudentCourse.query.delete()

            # Commit the changes
            db.session.commit()
            print("Successfully deleted all student course records!")

        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    cleanup_database()