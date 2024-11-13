from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import or_
import logging
import re
from models.models import db, User, Teacher, Student, Staff, Department, InstructorCourse, StudentCourse
from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

logging.basicConfig(level=logging.DEBUG)


def determine_user_type(username):
    """
    Determine user type based on username pattern:
    - S[number] for students (e.g., S12345)
    - T[number] for teachers (e.g., T12345)
    - ST[number] for staff (e.g., ST12345)
    """
    if username.startswith('S') and username[1:].isdigit():
        return 'student'
    elif username.startswith('T') and username[1:].isdigit():
        return 'teacher'
    elif username.startswith('ST') and username[2:].isdigit():
        return 'staff'
    return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    # Redirect if user is already logged in

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Login the user
            login_user(user)
            app.logger.info(f'User {username} logged in successfully')

            # Redirect based on user type
            if user.user_type == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.user_type == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.user_type == 'staff':
                return redirect(url_for('staff_dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('signin'))

    # GET request - show the login form
    return render_template('signin.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('signin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Determine user type from username
        user_type = determine_user_type(username)
        if not user_type:
            return jsonify({
                'success': False,
                'message': 'Invalid username format. Use S12345 for students, T12345 for teachers, A12345 for advisors, or ST12345 for staff'
            })

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'})

        # Create the user
        user = User(username=username, email=email, user_type=user_type)
        user.set_password(password)

        # Create corresponding role-specific record
        if user_type == 'student':
            student = Student(student_id=username)
            db.session.add(student)
        elif user_type == 'teacher':
            teacher = Teacher(instructor_id=username)
            db.session.add(teacher)
        elif user_type == 'staff':
            staff = Staff(staff_id=username)
            db.session.add(staff)

        db.session.add(user)

        try:
            db.session.commit()
            return redirect(url_for('signin'))
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})

    return render_template('signup.html')


@app.route('/search/courses', methods=['GET'])
@login_required
def search_courses():
    query = request.args.get('q', '')

    courses = InstructorCourse.query.filter(
        or_(
            InstructorCourse.course_prefix.ilike(f'%{query}%'),
            InstructorCourse.course_number.ilike(f'%{query}%')
        )
    ).all()

    results = []
    for course in courses:
        instructor = Teacher.query.filter_by(instructor_id=course.instructor_id).first()
        results.append({
            'prefix': course.course_prefix,
            'number': course.course_number,
            'credits': course.credits,
            'semester': course.semester,
            'year': course.year_taught,
            'instructor_id': course.instructor_id
        })

    return jsonify(results)


@app.route('/student/courses')
@login_required
def student_courses():
    if current_user.user_type != 'student':
        return redirect(url_for('index'))

    student = Student.query.filter_by(student_id=current_user.username).first()
    courses = StudentCourse.query.filter_by(student_id=student.student_id).all()
    return render_template('student_courses.html', courses=courses)


@app.route('/teacher/courses')
@login_required
def teacher_courses():
    if current_user.user_type != 'teacher':
        return redirect(url_for('index'))

    teacher = Teacher.query.filter_by(instructor_id=current_user.username).first()
    courses = InstructorCourse.query.filter_by(instructor_id=teacher.instructor_id).all()
    return render_template('teacher_courses.html', courses=courses)


@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.user_type != 'student':
        return redirect(url_for('index'))

    # Get student's information
    # Remove the .first() to see if we get any results at all
    student = Student.query.filter_by(student_id=current_user.username.replace('S', '')).first()

    if student:
        # Add debug print
        print(f"Found student: {student.student_id}")

        # Get all courses for this student
        courses = StudentCourse.query.filter_by(student_id=student.student_id).all()

        # Debug print courses
        print(f"Found {len(courses)} courses for student")
        for course in courses:
            print(
                f"Course: {course.course_prefix} {course.course_number} - {course.semester} {course.year_taken} - Grade: {course.grade}")

        # Calculate GPAs and credits
        grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        current_year = '2024'
        current_semester = 'S'

        # Separate current courses
        current_courses = [
            course for course in courses
            if course.year_taken == current_year and course.semester == current_semester
        ]

        # Calculate semester GPA
        semester_points = sum(grade_points.get(c.grade, 0) for c in current_courses if c.grade in grade_points)
        semester_count = sum(1 for c in current_courses if c.grade in grade_points)
        semester_gpa = round(semester_points / max(semester_count, 1), 2)

        # Calculate cumulative GPA
        total_points = sum(grade_points.get(c.grade, 0) for c in courses if c.grade in grade_points)
        total_count = sum(1 for c in courses if c.grade in grade_points)
        cumulative_gpa = round(total_points / max(total_count, 1), 2)

        # Calculate credits
        completed_credits = sum(3 for c in courses if c.grade in grade_points)  # Assuming 3 credits per course
        current_credits = sum(3 for c in current_courses if c.grade == 'IP')

        # Get department and advisor info
        department = Department.query.filter_by(department_id=student.major).first()
        advisor_phone = department.advisor_phone if department else 'Not Available'
        advisor_email = f"{department.advisor_id}@university.edu" if department else 'Not Available'

        # Debug print final data
        print(f"Semester GPA: {semester_gpa}")
        print(f"Cumulative GPA: {cumulative_gpa}")
        print(f"Completed Credits: {completed_credits}")
        print(f"Current Credits: {current_credits}")

        return render_template('student_dashboard.html',
                               current_user=current_user,
                               courses=courses,
                               gpa=semester_gpa,
                               cumulative_gpa=cumulative_gpa,
                               completed_credits=completed_credits,
                               current_credits=current_credits,
                               student=student,
                               advisor_phone=advisor_phone,
                               advisor_email=advisor_email)
    else:
        print(f"No student found for username: {current_user.username}")
    return render_template('student_dashboard.html', current_user=current_user)

# Add the debug route here
@app.route('/debug/student_data/<student_id>')
def debug_student_data(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        courses = StudentCourse.query.filter_by(student_id=student.student_id).all()
        return jsonify({
            'student_found': True,
            'student_id': student.student_id,
            'courses': [{
                'prefix': c.course_prefix,
                'number': c.course_number,
                'semester': c.semester,
                'year': c.year_taken,
                'grade': c.grade
            } for c in courses]
        })
    return jsonify({'student_found': False})


@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if current_user.user_type != 'teacher':
        return redirect(url_for('index'))

    teacher = Teacher.query.filter_by(instructor_id=current_user.username).first()

    if teacher:
        # Get teacher's courses
        courses = InstructorCourse.query.filter_by(instructor_id=teacher.instructor_id).all()

        # Get class rosters for each course and sort them
        course_rosters = {}
        for course in courses:
            students = StudentCourse.query.filter_by(
                course_prefix=course.course_prefix,
                course_number=course.course_number,
                semester=course.semester
            ).all()

            # Sort students by ID numerically
            sorted_students = sorted(students,
                                     key=lambda x: int(x.student_id.replace('U', '')) if x.student_id.startswith(
                                         'U') else float('inf'))

            course_rosters[f"{course.course_prefix} {course.course_number}"] = sorted_students

        return render_template('teacher_dashboard.html',
                               courses=courses,
                               course_rosters=course_rosters,
                               teacher=teacher)

    return render_template('teacher_dashboard.html')


@app.route('/update_grade', methods=['POST'])
@login_required
def update_grade():
    if current_user.user_type != 'teacher':
        return jsonify({'success': False, 'message': 'Unauthorized'})

    data = request.get_json()
    student_id = data.get('student_id')
    course_prefix = data.get('course_prefix')
    course_number = data.get('course_number')
    new_grade = data.get('grade')

    if new_grade not in ['A', 'B', 'C', 'D', 'F']:
        return jsonify({'success': False, 'message': 'Invalid grade'})

    course = StudentCourse.query.filter_by(
        student_id=student_id,
        course_prefix=course_prefix,
        course_number=course_number
    ).first()

    if course:
        course.grade = new_grade
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Course not found'})


@app.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if current_user.user_type != 'staff':
        return redirect(url_for('index'))
    return render_template('staff_dashboard.html')


@app.route('/advisor_dashboard')
@login_required
def advisor_dashboard():
    if current_user.user_type != 'advisor':
        return redirect(url_for('index'))
    return render_template('advisor_dashboard.html')


def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")


def fix_user_types():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        users = User.query.all()
        for user in users:
            correct_type = determine_user_type(user.username)
            if correct_type and user.user_type != correct_type:
                print(f"Fixing user type for {user.username} from {user.user_type} to {correct_type}")
                user.user_type = correct_type
        db.session.commit()
        print("User types fixed!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)