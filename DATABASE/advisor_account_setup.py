from flask import Flask
from models.models import db, Advisor, Department
from config.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def reset_and_populate_data():
    app = create_app()

    with app.app_context():
        print("Deleting existing data...")
        Advisor.query.delete()
        Department.query.delete()
        db.session.commit()

        # Create departments first
        departments_data = [
            ('D1', 'G', '233', 'ART', '126', 'A6', '1117'),
            ('D2', 'R', '1045', 'CS,IT,CyS,IS', '122', 'A1', '2002'),
            ('D3', 'H', '2120', 'EE,CpE', '124', 'A17', '3090'),
            ('D4', 'H', '1064', 'EDU', '120', 'A12', '7209'),
            ('D5', 'G', '118', 'MATH,MEDU', '120', 'A23', '4412'),
            ('D6', 'M', '36', 'SOC', '120', 'A15', '2710'),
            ('D7', 'G', '104', 'ACCT,MKT', '122', 'A16', '5110'),
            ('D8', 'M', '32', 'BIOL', '120', 'A17', '2800'),
            ('D9', 'H', '1152', 'PHY', '124', 'A26', '1528')
        ]

        for dept_id, building, office, majors, hours_req, advisor_id, advisor_phone in departments_data:
            department = Department(
                department_id=dept_id,
                building=building,
                office=office,
                major_offered=majors,
                total_hours_req=hours_req,
                advisor_id=advisor_id,
                advisor_phone=advisor_phone
            )
            db.session.add(department)

        # Create advisors with complete mapping
        advisors_data = [
            ('A1', 'D2', '2002', 'R 1045', 'CS'),
            ('A2', 'D2', '2324', 'R 1045', 'CS'),
            ('A3', 'D2', '2717', 'R 1045', 'CS'),
            ('A4', 'D2', '2888', 'R 1045', 'CS'),
            ('A5', 'D2', '2202', 'R 1045', 'CS'),
            ('A6', 'D1,D2', '2329', 'G 233', 'ART,CS'),
            ('A7', 'D3', '2555', 'H 2120', 'EE,CpE'),
            ('A8', 'D3', '2007', 'H 2120', 'EE,CpE'),
            ('A9', 'D7', '5116', 'G 104', 'MKT'),
            ('A11', 'D3', '3414', 'H 2120', 'EE,CpE'),
            ('A12', 'D4', '7209', 'H 1064', 'EDU'),
            ('A14', 'D5', '1445', 'G 118', 'MEDU'),
            ('A15', 'D6', '2710', 'M 36', 'SOC'),
            ('A16', 'D7', '5110', 'G 104', 'ACCT,MKT'),
            ('A17', 'D3,D8', '3090', 'H 2120,M 32', 'EE,CpE,BIOL'),
            ('A20', 'D3', '3311', 'H 2120', 'EE,CpE'),
            ('A22', 'D5', '4314', 'G 118', 'MATH'),
            ('A23', 'D5', '4412', 'G 118', 'MATH'),
            ('A25', 'D5', '4887', 'G 118', 'MATH'),
            ('A26', 'D9', '1528', 'H 1152', 'PHY')
        ]

        for advisor_id, dept_id, phone, office_loc, majors in advisors_data:
            advisor = Advisor(
                advisor_id=advisor_id,
                department_id=dept_id,
                phone=phone,
                office_location=office_loc,
                office_hours='Mon-Fri 9:00-11:00',
                max_students=50,
                current_students=0
            )
            db.session.add(advisor)

        try:
            db.session.commit()
            print("Database reset and populated successfully!")
            print(f"Created {len(departments_data)} departments")
            print(f"Created {len(advisors_data)} advisors")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")


if __name__ == '__main__':
    reset_and_populate_data()