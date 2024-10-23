import pandas as pd
from models.models import db, User, Teacher, Student, Staff, Department, InstructorCourse, StudentCourse
from flask import Flask
from config.config import Config
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def ensure_tables_exist(app):
    with app.app_context():
        print("Creating database tables...")
        try:
            db.create_all()
            print("Tables created successfully!")
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            raise


def import_instructors(excel_file):
    app = create_app()
    with app.app_context():
        print("Reading Instructors sheet...")
        df = pd.read_excel(excel_file, sheet_name='Instructors')
        print(f"Found {len(df)} instructors to import")

        for _, row in df.iterrows():
            print(f"Importing instructor: {row['InstructorID']}")
            teacher = Teacher(
                instructor_id=row['InstructorID'],
                instructor_phone=str(row['InstructorPhone']),
                department_id=row['DepartmentID'],
                hired_semester=row['HiredSemester']
            )
            db.session.add(teacher)

        try:
            db.session.commit()
            print("Instructors imported successfully!")
        except Exception as e:
            print(f"Error importing instructors: {str(e)}")
            db.session.rollback()
            raise


def import_students(excel_file):
    app = create_app()
    with app.app_context():
        print("Reading Students sheet...")
        df = pd.read_excel(excel_file, sheet_name='Students')
        print(f"Found {len(df)} students to import")

        for _, row in df.iterrows():
            print(f"Importing student: {row['StudentID']}")
            student = Student(
                student_id=row['StudentID'],
                gender=row['Gender'],
                major=row['Major']
            )
            db.session.add(student)

        try:
            db.session.commit()
            print("Students imported successfully!")
        except Exception as e:
            print(f"Error importing students: {str(e)}")
            db.session.rollback()
            raise


def import_staff(excel_file):
    app = create_app()
    with app.app_context():
        print("Reading Staff sheet...")
        df = pd.read_excel(excel_file, sheet_name='Staffs')
        print(f"Found {len(df)} staff members to import")

        for _, row in df.iterrows():
            print(f"Importing staff member: {row['StaffID']}")
            staff = Staff(
                staff_id=row['StaffID'],
                department_id=row['DepartmentID'],
                phone=str(row['Phone'])
            )
            db.session.add(staff)

        try:
            db.session.commit()
            print("Staff imported successfully!")
        except Exception as e:
            print(f"Error importing staff: {str(e)}")
            db.session.rollback()
            raise


def import_departments(excel_file):
    app = create_app()
    with app.app_context():
        print("Reading Departments sheet...")
        df = pd.read_excel(excel_file, sheet_name='Departments')
        print(f"Found departments to import")

        # Group by DepartmentID to handle multiple majors
        grouped = df.groupby('DepartmentID')

        for dept_id, group in grouped:
            first_row = group.iloc[0]
            print(f"Importing department: {dept_id}")

            # Convert all values to strings explicitly
            department = Department(
                department_id=str(dept_id),
                building=str(first_row['Building']),
                office=str(first_row['Office']),
                major_offered=','.join(str(x) for x in group['MajorOffered'].dropna().tolist()),
                total_hours_req=str(first_row['TotalHoursReq']),
                advisor_id=str(first_row['AdvisorID']),
                advisor_phone=str(first_row['AdvisorPhone'])
            )
            db.session.add(department)

        try:
            db.session.commit()
            print("Departments imported successfully!")
        except Exception as e:
            print(f"Error importing departments: {str(e)}")
            db.session.rollback()
            raise


def import_instructor_courses(excel_file):
    app = create_app()
    with app.app_context():
        print("Reading InstructorCourse sheet...")
        df = pd.read_excel(excel_file, sheet_name='InstructorCourse')
        print(f"Found {len(df)} instructor course records to import")

        for _, row in df.iterrows():
            print(f"Importing course for instructor {row['InstructorID']}: {row['CoursePrefix']} {row['CourseNumber']}")
            instructor_course = InstructorCourse(
                instructor_id=str(row['InstructorID']),
                course_prefix=str(row['CoursePrefix']),
                course_number=str(row['CourseNumber']),
                credits=str(row['Credits']),  # Changed to str()
                semester=str(row['Semester']),
                year_taught=str(row['YearTaught'])
            )
            db.session.add(instructor_course)

        try:
            db.session.commit()
            print("Instructor courses imported successfully!")
        except Exception as e:
            print(f"Error importing instructor courses: {str(e)}")
            db.session.rollback()
            raise


def import_student_courses(excel_file):
    app = create_app()
    with app.app_context():
        print("Reading StudentCourse sheet...")
        df = pd.read_excel(excel_file, sheet_name='StudentCourse')
        print(f"Found {len(df)} student course records to import")

        for _, row in df.iterrows():
            print(f"Importing course for student {row['StudentID']}: {row['CoursePrefix']} {row['CourseNumber']}")
            student_course = StudentCourse(
                student_id=str(row['StudentID']),
                course_prefix=str(row['CoursePrefix']),
                course_number=str(row['CourseNumber']),
                semester=str(row['Semester']),
                year_taken=str(row['YearTaken']),
                grade=str(row['Grade'])
            )
            db.session.add(student_course)

        try:
            db.session.commit()
            print("Student courses imported successfully!")
        except Exception as e:
            print(f"Error importing student courses: {str(e)}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    try:
        excel_file = 'StudentsCourses.xlsx'  # Make sure this matches your file name
        print("What would you like to import?")
        print("1. Instructors")
        print("2. Students")
        print("3. Staff")
        print("4. Departments")
        print("5. Instructor Courses")
        print("6. Student Courses")
        print("7. All")
        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            import_instructors(excel_file)
        elif choice == '2':
            import_students(excel_file)
        elif choice == '3':
            import_staff(excel_file)
        elif choice == '4':
            import_departments(excel_file)
        elif choice == '5':
            import_instructor_courses(excel_file)
        elif choice == '6':
            import_student_courses(excel_file)
        elif choice == '7':
            import_instructors(excel_file)
            import_students(excel_file)
            import_staff(excel_file)
            import_departments(excel_file)
            import_instructor_courses(excel_file)
            import_student_courses(excel_file)
        else:
            print("Invalid choice!")

    except Exception as e:
        print(f"Fatal error: {str(e)}")