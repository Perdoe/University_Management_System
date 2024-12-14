# University Management System

A comprehensive web-based university management system built with Flask and React, featuring role-based access control and modular architecture.

## Overview

This system provides a unified platform for managing university operations, with separate interfaces for:
- Students (course registration, grade viewing, GPA calculation)
- Teachers (course management, grade submission)
- Staff (administrative tasks, department management)
- Advisors (student advising, course approval)

## Architecture

### Backend (Flask)
- **Models**: SQLAlchemy models for users, courses, departments, and more
- **Authentication**: Flask-Login for session management
- **Database**: PostgreSQL for data persistence
- **API**: RESTful endpoints for different user roles

### Frontend
- **React Components**: Role-specific dashboards
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React hooks for local state management

## Key Features

### For Students
- View current courses and grades
- Calculate semester and cumulative GPA
- Access transcript information
- Contact advisors
- Update profile settings

### For Teachers
- Manage course rosters
- Submit and update grades
- View teaching schedule
- Access department information

### For Staff
- Manage department data
- Monitor system logs
- Generate reports
- Update student and course information

### For Advisors
- View student academic progress
- Approve course registrations
- Manage degree plans
- Schedule appointments

## Setup and Installation

1. Clone the repository
2. Set up the virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Initialize the database:
```bash
python main.py
```

6. Run the development server:
```bash
flask run
```

## Database Schema

The system uses the following main tables:
- Users
- Students
- Teachers
- Staff
- Departments
- Courses
- StudentCourses
- InstructorCourses
- SystemLogs

## Authentication

Users are identified by their ID format:
- Students: S12345
- Teachers: T12345
- Staff: ST12345
- Advisors: A12345

## Security Features

- Password hashing using Werkzeug
- Role-based access control
- Session management
- Input validation
- Error logging
- Activity monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## Testing

Run the test suite:
```bash
python -m pytest tests/
```
