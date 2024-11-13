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
        print("Reading Staffs sheet...")  # Updated sheet name reference

        # Clear existing records first
        print("Clearing existing staff records...")
        Staff.query.delete()
        db.session.commit()

        try:
            # Read the Excel file with correct sheet name
            df = pd.read_excel(excel_file, sheet_name='Staffs')  # Changed from 'Staff' to 'Staffs'
            print(f"Found {len(df)} staff records to import")

            # Create a list to store all records for batch insert
            staff_records = []

            # Process each row
            for _, row in df.iterrows():
                if pd.notna(row['StaffID']):
                    # Create new staff record
                    staff = Staff(
                        staff_id=str(row['StaffID'])[:10],  # Ensure within varchar(10)
                        department_id=str(row['DepartmentID'])[:10],  # Ensure within varchar(10)
                        phone=str(row['Phone'])[:20] if pd.notna(row['Phone']) else None  # Ensure within varchar(20)
                    )
                    staff_records.append(staff)
                    print(f"Adding staff member {row['StaffID']} from department {row['DepartmentID']}")

            # Batch insert all records
            db.session.bulk_save_objects(staff_records)
            db.session.commit()
            print("\nStaff records imported successfully!")

            # Verify the import
            verify_staff()

        except Exception as e:
            print(f"Error importing staff: {str(e)}")
            db.session.rollback()
            raise


def verify_staff():
    """Verify the imported staff records"""
    app = create_app()
    with app.app_context():
        print("\nStaff Records:")
        print("-" * 50)

        staff_members = Staff.query.order_by(Staff.staff_id).all()

        if staff_members:
            for staff in staff_members:
                print(f"""
Staff ID: {staff.staff_id}
Department: {staff.department_id}
Phone: {staff.phone if staff.phone else 'Not provided'}
{'-' * 30}""")
            print(f"\nTotal staff members: {len(staff_members)}")
        else:
            print("No staff records found in database.")


def count_staff_by_department():
    """Show count of staff members per department"""
    app = create_app()
    with app.app_context():
        print("\nStaff Count by Department:")
        print("-" * 50)

        departments = db.session.query(Staff.department_id, db.func.count(Staff.id)) \
            .group_by(Staff.department_id) \
            .order_by(Staff.department_id) \
            .all()

        for dept_id, count in departments:
            print(f"Department {dept_id}: {count} staff members")


def import_departments(excel_file):
    app = create_app()
    with app.app_context():
        print("Reading Departments sheet...")

        # First, delete existing departments
        print("Clearing existing department records...")
        Department.query.delete()
        db.session.commit()

        # Create departments with proper length constraints
        departments_data = [
            {
                'department_id': 'D1',
                'building': 'G',
                'office': '233',
                'major_offered': 'ART,CS',  # Store as single string
                'total_hours_req': '126',
                'advisor_id': 'A6',
                'advisor_phone': '1117'
            },
            {
                'department_id': 'D2',
                'building': 'R',
                'office': '1045',
                'major_offered': 'IT,CyS,IS',
                'total_hours_req': '122',
                'advisor_id': 'A1',
                'advisor_phone': '2002'
            },
            {
                'department_id': 'D3',
                'building': 'H',
                'office': '2120',
                'major_offered': 'EE,CpE',
                'total_hours_req': '124',
                'advisor_id': 'A17',
                'advisor_phone': '3690'
            },
            {
                'department_id': 'D4',
                'building': 'H',
                'office': '1064',
                'major_offered': 'EDU',
                'total_hours_req': '120',
                'advisor_id': 'A12',
                'advisor_phone': '7209'
            },
            {
                'department_id': 'D5',
                'building': 'G',
                'office': '118',
                'major_offered': 'MATH,MEDU',
                'total_hours_req': '120',
                'advisor_id': 'A23',
                'advisor_phone': '4412'
            },
            {
                'department_id': 'D6',
                'building': 'M',
                'office': '36',
                'major_offered': 'SOC',
                'total_hours_req': '120',
                'advisor_id': 'A15',
                'advisor_phone': '2710'
            },
            {
                'department_id': 'D7',
                'building': 'G',
                'office': '104',
                'major_offered': 'ACCT,MKT',
                'total_hours_req': '122',
                'advisor_id': 'A16',
                'advisor_phone': '5110'
            },
            {
                'department_id': 'D8',
                'building': 'M',
                'office': '32',
                'major_offered': 'BIOL',
                'total_hours_req': '120',
                'advisor_id': 'A17',
                'advisor_phone': '2800'
            },
            {
                'department_id': 'D9',
                'building': 'H',
                'office': '1152',
                'major_offered': 'PHY',
                'total_hours_req': '124',
                'advisor_id': 'A26',
                'advisor_phone': '1528'
            }
        ]

        try:
            for dept_data in departments_data:
                # Create department record with explicit length checks
                department = Department(
                    department_id=dept_data['department_id'][:10],  # Ensure max length of 10
                    building=dept_data['building'][:10],
                    office=dept_data['office'][:20],
                    major_offered=dept_data['major_offered'],  # This is text type, no length limit
                    total_hours_req=dept_data['total_hours_req'][:10],
                    advisor_id=dept_data['advisor_id'][:10],
                    advisor_phone=dept_data['advisor_phone'][:20]
                )
                db.session.add(department)
                print(f"Adding department: {dept_data['department_id']}")

            db.session.commit()
            print("\nDepartments imported successfully!")

            # Verify the import
            departments = Department.query.all()
            print("\nVerifying imported departments:")
            print("-" * 50)
            for dept in departments:
                print(f"""
Department ID: {dept.department_id}
Building: {dept.building}
Office: {dept.office}
Majors Offered: {dept.major_offered}
Total Hours Required: {dept.total_hours_req}
Advisor ID: {dept.advisor_id}
Advisor Phone: {dept.advisor_phone}
{'-' * 50}""")

        except Exception as e:
            print(f"Error importing departments: {str(e)}")
            db.session.rollback()
            raise


def verify_departments():
    """Verify the imported departments"""
    app = create_app()
    with app.app_context():
        departments = Department.query.order_by(Department.department_id).all()
        print("\nDepartment Records:")
        print("-" * 50)
        for dept in departments:
            print(f"""
Department ID: {dept.department_id}
Building: {dept.building}
Office: {dept.office}
Majors Offered: {dept.major_offered}
Total Hours Required: {dept.total_hours_req}
Advisor ID: {dept.advisor_id}
Advisor Phone: {dept.advisor_phone}
{'-' * 50}""")


def import_instructor_courses(excel_file):
    app = create_app()
    with app.app_context():
        print("Reading InstructorCourse sheet...")

        # Clear existing records first
        print("Clearing existing instructor course records...")
        InstructorCourse.query.delete()
        db.session.commit()

        try:
            # Read the Excel file
            df = pd.read_excel(excel_file, sheet_name='InstructorCourse')
            print(f"Found {len(df)} instructor course records to import")

            # Create a list to store all records for batch insert
            course_records = []

            # Keep track of the current instructor ID
            current_id = None

            # Process each row
            for _, row in df.iterrows():
                # If we have an instructor ID in this row, use it as the current ID
                if pd.notna(row['InstructorID']):
                    current_id = str(row['InstructorID'])

                if current_id and pd.notna(row['CoursePrefix']):
                    # Create new instructor course record
                    instructor_course = InstructorCourse(
                        instructor_id=current_id,
                        course_prefix=str(row['CoursePrefix'])[:10],  # Ensure within varchar(10)
                        course_number=str(row['CourseNumber'])[:10],  # Ensure within varchar(10)
                        credits=str(row['Credits'])[:5],  # Ensure within varchar(5)
                        semester=str(row['Semester'])[:5],  # Ensure within varchar(5)
                        year_taught=str(row['YearTaught'])[:10]  # Ensure within varchar(10)
                    )
                    course_records.append(instructor_course)
                    print(f"Adding course {row['CoursePrefix']} {row['CourseNumber']} for instructor {current_id}")

            # Batch insert all records
            db.session.bulk_save_objects(course_records)
            db.session.commit()
            print("\nInstructor courses imported successfully!")

            # Verify the import
            verify_instructor_courses()

        except Exception as e:
            print(f"Error importing instructor courses: {str(e)}")
            db.session.rollback()
            raise


def verify_instructor_courses():
    """Verify the imported instructor courses"""
    app = create_app()
    with app.app_context():
        print("\nInstructor Course Distribution:")
        print("-" * 50)

        # Get all unique instructor IDs
        instructors = db.session.query(InstructorCourse.instructor_id) \
            .distinct() \
            .order_by(InstructorCourse.instructor_id) \
            .all()

        for (instructor_id,) in instructors:
            courses = InstructorCourse.query \
                .filter_by(instructor_id=instructor_id) \
                .order_by(
                InstructorCourse.year_taught,
                InstructorCourse.semester,
                InstructorCourse.course_prefix,
                InstructorCourse.course_number
            ).all()

            if courses:
                print(f"\nInstructor {instructor_id} - {len(courses)} courses:")
                print("-" * 30)
                for course in courses:
                    print(
                        f"  {course.course_prefix} {course.course_number:5} - "
                        f"{course.credits} credits - "
                        f"{course.semester} {course.year_taught}"
                    )


def import_student_courses(excel_file):
    app = create_app()
    with app.app_context():
        print("Reading StudentCourse sheet...")
        df = pd.read_excel(excel_file, sheet_name='StudentCourse')

        print("Clearing existing student course records...")
        StudentCourse.query.delete()
        db.session.commit()

        # Create a list to store records for batch insert
        course_records = []

        # Keep track of the current student ID
        current_id = None

        # Process each row
        for _, row in df.iterrows():
            # If we have a student ID in this row, use it as the current ID
            if pd.notna(row['StudentID']):
                current_id = str(row['StudentID'])

            if current_id:
                student_course = StudentCourse(
                    student_id=current_id,
                    course_prefix=str(row['CoursePrefix']),
                    course_number=str(row['CourseNumber']),
                    semester=str(row['Semester']),
                    year_taken=str(row['YearTaken']),
                    grade=str(row['Grade'])
                )
                course_records.append(student_course)
                print(f"Adding course {row['CoursePrefix']} {row['CourseNumber']} for student {current_id}")

        # Batch insert all records
        try:
            db.session.bulk_save_objects(course_records)
            db.session.commit()
            print("\nSuccessfully imported all student courses!")

            # Print summary
            with app.app_context():
                for i in range(1, 21):  # U1 through U20
                    student_id = f'U{i}'
                    count = StudentCourse.query.filter_by(student_id=student_id).count()
                    if count > 0:
                        print(f"Student {student_id}: {count} courses")

        except Exception as e:
            print(f"Error importing student courses: {str(e)}")
            db.session.rollback()
            raise


def verify_student_courses():
    """Verify the imported courses"""
    app = create_app()
    with app.app_context():
        print("\nCourse Distribution by Student (U1-U20):")
        print("-" * 50)

        for i in range(1, 21):  # U1 through U20
            student_id = f'U{i}'
            courses = StudentCourse.query.filter_by(student_id=student_id).order_by(
                StudentCourse.year_taken,
                StudentCourse.semester
            ).all()

            if courses:
                print(f"\nStudent {student_id} - {len(courses)} courses:")
                print("-" * 30)
                for course in courses:
                    print(
                        f"  {course.course_prefix} {course.course_number:5} - {course.semester} {course.year_taken} - Grade: {course.grade}")


def count_courses_per_student():
    """Show a simple count of courses per student"""
    app = create_app()
    with app.app_context():
        print("\nCourse Count per Student:")
        print("-" * 50)

        for i in range(1, 21):  # U1 through U20
            student_id = f'U{i}'
            count = StudentCourse.query.filter_by(student_id=student_id).count()
            if count > 0:
                print(f"Student {student_id}: {count} courses")
            else:
                print(f"Student {student_id}: No courses")


if __name__ == '__main__':
    try:
        excel_file = 'StudentsCourses.xlsx'  # Make sure this matches your file name
        print("\nUniversity Database Management System")
        print("=" * 40)
        print("1. Import student courses")
        print("2. Verify course distribution")
        print("3. Show course count per student")
        print("4. Import/Update departments")
        print("5. Import instructor courses")
        print("6. Verify instructor courses")
        print("7. Import staff records")
        print("8. Verify staff records")
        print("9. Show staff count by department")
        choice = input("\nEnter your choice (1-9): ")

        if choice == '1':
            import_student_courses(excel_file)
        elif choice == '2':
            verify_student_courses()
        elif choice == '3':
            count_courses_per_student()
        elif choice == '4':
            import_departments(excel_file)
            print("\nDepartment import completed!")
            print("\nWould you like to verify the department import?")
            verify = input("Enter 'y' for yes, any other key to exit: ").lower()
            if verify == 'y':
                verify_departments()
        elif choice == '5':
            import_instructor_courses(excel_file)
        elif choice == '6':
            verify_instructor_courses()
        elif choice == '7':
            import_staff(excel_file)
        elif choice == '8':
            verify_staff()
        elif choice == '9':
            count_staff_by_department()
        else:
            print("\nInvalid choice! Please select a number between 1 and 9.")

    except Exception as e:
        print(f"\nFatal error: {str(e)}")
    finally:
        print("\nProgram completed. Press any key to exit.")
        input()