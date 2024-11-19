from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import or_
import logging
import re
from models.models import db, User, Advisor, Teacher, Student, Staff, Department, InstructorCourse, StudentCourse, SystemLog
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
    elif username.startswith('A') and username[1:].isdigit():
        return 'advisor'
    return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)

            # Add this logging call
            log_activity(
                user_id=username,
                activity="User Login",
                details=f"User {username} logged in successfully",
                status='success'
            )

            if user.user_type == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.user_type == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.user_type == 'staff':
                return redirect(url_for('staff_dashboard'))
            elif user.user_type == 'advisor':
                return redirect(url_for('advisor_dashboard'))
        else:
            # Add this logging call for failed attempts
            log_activity(
                user_id=username,
                activity="Failed Login",
                details=f"Failed login attempt for username {username}",
                status='error'
            )
            flash('Invalid username or password', 'error')
            return redirect(url_for('signin'))

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

    student = Student.query.filter_by(student_id=current_user.username.replace('S', '')).first()

    if student:
        courses = StudentCourse.query.filter_by(student_id=student.student_id).all()

        # Calculate GPAs and credits
        grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        current_year = '2024'
        current_semester = 'S'

        current_courses = [course for course in courses
                           if course.year_taken == current_year and course.semester == current_semester]

        semester_points = sum(grade_points.get(c.grade, 0) for c in current_courses if c.grade in grade_points)
        semester_count = sum(1 for c in current_courses if c.grade in grade_points)
        semester_gpa = round(semester_points / max(semester_count, 1), 2)

        total_points = sum(grade_points.get(c.grade, 0) for c in courses if c.grade in grade_points)
        total_count = sum(1 for c in courses if c.grade in grade_points)
        cumulative_gpa = round(total_points / max(total_count, 1), 2)

        completed_credits = sum(3 for c in courses if c.grade in grade_points)
        current_credits = sum(3 for c in current_courses if c.grade == 'IP')

        # Get department and advisor info
        department = Department.query.filter(
            Department.major_offered.like(f"%{student.major}%")
        ).first()

        if department:
            office_location = f"{department.building} {department.office}"
            advisor_phone = department.advisor_phone
            advisor_email = f"{department.advisor_id}@university.edu"
        else:
            office_location = 'Not Available'
            advisor_phone = 'Not Available'
            advisor_email = 'Not Available'

        return render_template('student_dashboard.html',
                               current_user=current_user,
                               courses=courses,
                               gpa=semester_gpa,
                               cumulative_gpa=cumulative_gpa,
                               completed_credits=completed_credits,
                               current_credits=current_credits,
                               student=student,
                               office_location=office_location,
                               advisor_phone=advisor_phone,
                               advisor_email=advisor_email)

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


@app.route('/api/student/update-profile', methods=['POST'])
@login_required
def update_student_profile():
    if current_user.user_type != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    new_email = data.get('email')

    # Verify current password
    if not current_user.check_password(current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

    try:
        if new_email:
            # Check if email already exists for another user
            existing_user = User.query.filter(
                User.email == new_email,
                User.id != current_user.id
            ).first()
            if existing_user:
                return jsonify({'success': False, 'message': 'Email already in use'}), 400
            current_user.email = new_email

        if new_password:
            current_user.set_password(new_password)

        db.session.commit()

        # Log the profile update
        log_activity(
            current_user.username,
            "Profile Update",
            f"Student {current_user.username} updated their profile",
            "success"
        )

        return jsonify({'success': True, 'message': 'Profile updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/teacher/update-profile', methods=['POST'])
@login_required
def update_teacher_profile():
    print("Teacher profile update requested")  # Debug log
    if current_user.user_type != 'teacher':
        print(f"Unauthorized: user type is {current_user.user_type}")  # Debug log
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        print("Received data:", data)  # Debug log

        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        new_email = data.get('email')

        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

        if new_email:
            # Check if email already exists for another user
            existing_user = User.query.filter(
                User.email == new_email,
                User.id != current_user.id
            ).first()
            if existing_user:
                return jsonify({'success': False, 'message': 'Email already in use'}), 400
            current_user.email = new_email

        if new_password:
            current_user.set_password(new_password)

        db.session.commit()

        # Log the profile update
        log_activity(
            current_user.username,
            "Profile Update",
            f"Teacher {current_user.username} updated their profile",
            "success"
        )

        return jsonify({'success': True, 'message': 'Profile updated successfully'})

    except Exception as e:
        print(f"Error in profile update: {str(e)}")  # Debug log
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

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
        old_grade = course.grade
        course.grade = new_grade
        db.session.commit()

        # Log the grade change
        log_activity(
            current_user.username,
            "Grade Update",
            f"Changed grade for {student_id} in {course_prefix} {course_number} from {old_grade} to {new_grade}"
        )

        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Course not found'})


@app.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if current_user.user_type != 'staff':
        return redirect(url_for('index'))

    staff = Staff.query.filter_by(staff_id=current_user.username).first()
    courses = InstructorCourse.query.all()
    students = Student.query.all()

    # Add some debug printing
    system_logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(50).all()
    print(f"Found {len(system_logs)} logs")  # Debug print
    for log in system_logs:
        print(f"Log: {log.timestamp} - {log.user_id} - {log.activity}")  # Debug print

    department_stats = {
        'total_courses': len(courses),
        'total_faculty': len(Teacher.query.all()),
        'active_students': len(students),
        'available_seats': 1250
    }

    return render_template('staff_dashboard.html',
                         current_user=current_user,
                         staff=staff,
                         courses=courses,
                         students=students,
                         department_stats=department_stats,
                         system_logs=system_logs)


@app.route('/update_student_major', methods=['POST'])
@login_required
def update_student_major():
    if current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'})

    try:
        data = request.get_json()
        student_id = data.get('student_id')
        new_major = data.get('new_major')

        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            student.major = new_major
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Student not found'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# Add route for updating student major
@app.route('/update_major', methods=['POST'])
@login_required
def update_major():
    if current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    student_id = data.get('student_id')
    new_major = data.get('major')

    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        student.major = new_major
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Student not found'})


# Add route for assigning instructor
@app.route('/assign_instructor', methods=['POST'])
@login_required
def assign_instructor():
    if current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    course_prefix = data.get('course_prefix')
    course_number = data.get('course_number')
    instructor_id = data.get('instructor_id')

    course = InstructorCourse.query.filter_by(
        course_prefix=course_prefix,
        course_number=course_number
    ).first()

    if course:
        course.instructor_id = instructor_id
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Course not found'})


@app.route('/api/staff/department_data')
@login_required
def get_department_data():
    if current_user.user_type != 'staff':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Fetch actual data from your database
        return jsonify({
            'courseOfferings': {
                'totalActiveCourses': 42,
                'availableSeats': 1250
            },
            'faculty': {
                'totalFaculty': 15,
                'averageCourseLoad': 3.2
            },
            'requirements': {
                'requiredCredits': 120,
                'coreCourses': 45
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/update-profile', methods=['POST'])
@login_required
def update_staff_profile():
    if current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    new_email = data.get('email')

    # Verify current password
    if not current_user.check_password(current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

    try:
        if new_email:
            # Check if email already exists for another user
            existing_user = User.query.filter(
                User.email == new_email,
                User.id != current_user.id
            ).first()
            if existing_user:
                return jsonify({'success': False, 'message': 'Email already in use'}), 400
            current_user.email = new_email

        if new_password:
            current_user.set_password(new_password)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/staff/department-info')
@login_required
def get_department_info():
    if current_user.user_type != 'staff':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        department = Department.query.first()
        courses = InstructorCourse.query.all()
        teachers = Teacher.query.all()

        return jsonify({
            'courseOfferings': {
                'totalActiveCourses': len(courses),
                'availableSeats': 1250  # This should be calculated based on your data
            },
            'faculty': {
                'totalFaculty': len(teachers),
                'averageCourseLoad': round(len(courses) / len(teachers), 1) if teachers else 0
            },
            'requirements': {
                'requiredCredits': department.total_hours_req if department else 120,
                'coreCourses': 45  # This should come from your data
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/staff/performance-data')
@login_required
def get_performance_data():
    if current_user.user_type != 'staff':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # This should be calculated from your actual data
        performance_data = [
            {'month': 'Jan', 'avgGPA': 3.2, 'enrollment': 450},
            {'month': 'Feb', 'avgGPA': 3.3, 'enrollment': 448},
            {'month': 'Mar', 'avgGPA': 3.1, 'enrollment': 445}
        ]
        return jsonify(performance_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/advisor_dashboard')
@login_required
def advisor_dashboard():
    if current_user.user_type != 'advisor':
        return redirect(url_for('index'))

    departments = Department.query.filter_by(advisor_id=current_user.username).all()

    if departments:
        all_majors = []
        for dept in departments:
            majors = dept.major_offered.split(',')
            all_majors.extend([m.strip() for m in majors])

        # Get students with their courses
        students_data = []
        students = Student.query.filter(Student.major.in_(all_majors)).all()

        for student in students:
            courses = StudentCourse.query.filter_by(student_id=student.student_id).all()

            # Calculate GPA
            grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
            total_points = sum(grade_points.get(c.grade, 0) for c in courses if c.grade in grade_points)
            completed_courses = sum(1 for c in courses if c.grade in grade_points)
            gpa = round(total_points / completed_courses, 2) if completed_courses > 0 else 0.00

            # Calculate completed credits (assuming 3 credits per course)
            credits = completed_courses * 3

            students_data.append({
                'student_id': student.student_id,
                'major': student.major,
                'gpa': gpa,
                'credits_completed': credits
            })

    else:
        students_data = []

    # Rest of the code remains the same
    appointments = {'today': 0, 'week': 0, 'pending': 0}
    appointments_list = []
    degree_plans = {'active': 0, 'pending': 0, 'graduating': 0}
    registrations = []

    return render_template('advisor_dashboard.html',
                           current_user=current_user,
                           departments=departments,
                           students=students_data,
                           appointments=appointments,
                           appointments_list=appointments_list,
                           degree_plans=degree_plans,
                           registrations=registrations)


@app.route('/api/advisor/update-profile', methods=['POST'])
@login_required
def update_advisor_profile():
    if current_user.user_type != 'advisor':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    new_email = data.get('email')

    if not current_user.check_password(current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

    try:
        if new_email:
            existing_user = User.query.filter(
                User.email == new_email,
                User.id != current_user.id
            ).first()
            if existing_user:
                return jsonify({'success': False, 'message': 'Email already in use'}), 400
            current_user.email = new_email

        if new_password:
            current_user.set_password(new_password)

        db.session.commit()

        # Log the profile update
        log_activity(
            current_user.username,
            "Profile Update",
            f"Advisor {current_user.username} updated their profile",
            "success"
        )

        return jsonify({'success': True, 'message': 'Profile updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/advisor/students')
@login_required
def get_advisor_students():
    if current_user.user_type != 'advisor':
        return jsonify({'error': 'Unauthorized'}), 403

    advisor = Advisor.query.filter_by(advisor_id=current_user.username).first()
    students = Student.query.filter_by(major=advisor.department_id).all()

    return jsonify({
        'students': [{
            'id': student.student_id,
            'major': student.major,
            'gender': student.gender
        } for student in students]
    })

def log_activity(user_id, activity, details, status='success'):
    """Add a new log entry"""
    log = SystemLog(
        user_id=user_id,
        activity=activity,
        details=details,
        status=status
    )
    db.session.add(log)
    db.session.commit()

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