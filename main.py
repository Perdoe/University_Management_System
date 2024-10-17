from flask import Flask, render_template, request, jsonify, redirect, url_for
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def index():
    app.logger.info('Accessed index page')
    return render_template('index.html')


@app.route('/signin')
def signin():
    app.logger.info('Accessed signin page')
    return render_template('signin.html')


@app.route('/process_signin', methods=['POST'])
def process_signin():
    app.logger.info('Processing signin')
    try:
        user_type = request.form.get('user_type')
        username = request.form.get('username')
        password = request.form.get('password')

        app.logger.debug(f'Signin attempt - Type: {user_type}, Username: {username}')

        if user_type == 'student':
            return jsonify({'success': True, 'redirect': url_for('student_dashboard')})
        elif user_type == 'advisor':
            return jsonify({'success': True, 'redirect': url_for('advisor_dashboard')})
        elif user_type == 'teacher':
            return jsonify({'success': True, 'redirect': url_for('teacher_dashboard')})
        elif user_type == 'staff':
            return jsonify({'success': True, 'redirect': url_for('staff_dashboard')})
        else:
            app.logger.warning(f'Invalid user type: {user_type}')
            return jsonify({'success': False, 'message': 'Invalid user type'})
    except Exception as e:
        app.logger.error(f'Error in process_signin: {str(e)}')
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@app.route('/student')
def student_dashboard():
    app.logger.info('Accessed student dashboard')
    return render_template('student_dashboard.html')


@app.route('/advisor')
def advisor_dashboard():
    app.logger.info('Accessed advisor dashboard')
    return render_template('advisor_dashboard.html')


@app.route('/teacher')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

@app.route('/staff')
def staff_dashboard():
    return render_template('staff_dashboard.html')



if __name__ == '__main__':
    app.run(debug=True)