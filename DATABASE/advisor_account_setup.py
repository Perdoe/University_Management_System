import pandas as pd
from models.models import db, User, Advisor
from flask import Flask
from config.config import Config
import secrets
import string


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def generate_temporary_password():
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(10))


def fill_missing_advisor_info(df):
    """Fill in missing advisor information based on patterns in the data"""
    # Create department mapping
    dept_info = {}

    # First pass: collect all known department information
    for _, row in df.iterrows():
        if pd.notna(row['DepartmentID']):
            dept_info[row['DepartmentID']] = {
                'building': row['Building'],
                'office': row['Office'],
                'majors': []
            }
            if pd.notna(row['MajorOffered']):
                dept_info[row['DepartmentID']]['majors'].append(row['MajorOffered'])

    # Create advisor mapping
    advisor_info = {}

    # Map each advisor to their department
    for _, row in df.iterrows():
        advisor_cols = [col for col in row.index if col.startswith('AdvisorID')]
        phone_cols = [col for col in row.index if col.startswith('AdvisorPhone')]

        for id_col, phone_col in zip(advisor_cols, phone_cols):
            if pd.notna(row[id_col]):
                advisor_id = str(row[id_col])
                dept_id = row['DepartmentID']

                if advisor_id not in advisor_info:
                    advisor_info[advisor_id] = {
                        'department_id': dept_id,
                        'phone': str(row[phone_col]) if pd.notna(row[phone_col]) else None,
                        'building': row['Building'] if pd.notna(row['Building']) else None,
                        'office': row['Office'] if pd.notna(row['Office']) else None
                    }

    # Second pass: fill in missing information
    for advisor_id, info in advisor_info.items():
        if info['building'] is None or info['office'] is None:
            dept = info['department_id']
            if dept in dept_info:
                if info['building'] is None:
                    info['building'] = dept_info[dept]['building']
                if info['office'] is None:
                    info['office'] = dept_info[dept]['office']

    # Create the corrected dataframe rows
    corrected_rows = []

    for _, row in df.iterrows():
        new_row = row.copy()
        advisor_cols = [col for col in row.index if col.startswith('AdvisorID')]

        for id_col in advisor_cols:
            if pd.notna(row[id_col]):
                advisor_id = str(row[id_col])
                if advisor_id in advisor_info:
                    if pd.isna(new_row['Building']):
                        new_row['Building'] = advisor_info[advisor_id]['building']
                    if pd.isna(new_row['Office']):
                        new_row['Office'] = advisor_info[advisor_id]['office']

        corrected_rows.append(new_row)

    corrected_df = pd.DataFrame(corrected_rows, columns=df.columns)

    # Print summary of fixes
    print("\nFixes applied:")
    print("-" * 50)
    for advisor_id, info in advisor_info.items():
        print(f"Advisor {advisor_id}:")
        print(f"  Department: {info['department_id']}")
        print(f"  Building: {info['building']}")
        print(f"  Office: {info['office']}")
        print(f"  Phone: {info['phone']}")
        print("-" * 30)

    return corrected_df


def map_advisors_to_departments(df):
    """Create a mapping of advisors to their correct departments"""
    advisor_dept_map = {}

    # Iterate through each row in the dataframe
    for _, row in df.iterrows():
        dept_id = row['DepartmentID']
        building = row['Building']
        office = row['Office']

        # Get all advisor columns for this row
        advisor_cols = []
        phone_cols = []

        # Get column names dynamically
        for col in row.index:
            if col.startswith('AdvisorID') and pd.notna(row[col]):
                advisor_cols.append(col)
                # Find corresponding phone column
                phone_col = f"AdvisorPhone{col[9:]}" if col != "AdvisorID" else "AdvisorPhone"
                phone_cols.append(phone_col)

        # Map each advisor in this row to the department info
        for adv_col, phone_col in zip(advisor_cols, phone_cols):
            if pd.notna(row[adv_col]):
                advisor_id = str(row[adv_col]).strip()
                phone = str(row[phone_col]).strip() if pd.notna(row[phone_col]) else ''

                # Store the mapping with explicit department info
                advisor_dept_map[advisor_id] = {
                    'department_id': dept_id,
                    'building': building,
                    'office': str(office),
                    'phone': phone,
                    'office_location': f"{building} {office}"
                }

                print(f"DEBUG: Mapping advisor {advisor_id}:")
                print(f"  Department: {dept_id}")
                print(f"  Building: {building}")
                print(f"  Office: {office}")
                print(f"  Phone: {phone}")
                print("-" * 20)

    return advisor_dept_map


def update_advisor_data(df):
    """Update advisor data with correct department mappings"""
    print("\nStarting advisor mapping process...")
    print("Found departments:", df['DepartmentID'].unique())

    # Print the first few rows of the dataframe for debugging
    print("\nFirst few rows of department data:")
    print(df[['DepartmentID', 'Building', 'Office', 'AdvisorID', 'AdvisorPhone']].head())

    # Get the advisor to department mapping
    advisor_mappings = map_advisors_to_departments(df)

    if not advisor_mappings:
        print("WARNING: No advisor mappings were created!")

    print("\nMapped Advisor Information:")
    print("-" * 50)
    for advisor_id, info in advisor_mappings.items():
        print(f"Advisor {advisor_id}:")
        print(f"  Department: {info['department_id']}")
        print(f"  Building: {info['building']}")
        print(f"  Office: {info['office']}")
        print(f"  Phone: {info['phone']}")
        print(f"  Full Office Location: {info['office_location']}")
        print("-" * 30)

    return advisor_mappings

# Update your create_advisor_accounts function to use this mapping:
def create_advisor_accounts(excel_file):
    app = create_app()

    with app.app_context():
        print("Creating advisor accounts...")
        # Read department data
        df = pd.read_excel(excel_file, sheet_name='Departments')

        # Get advisor mappings
        print("\nAnalyzing department and advisor data...")
        advisor_mappings = update_advisor_data(df)

        # Keep track of created accounts
        created_accounts = []
        skipped_accounts = []

        for advisor_id, advisor_info in advisor_mappings.items():
            username = advisor_id

            # Check if user account already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                skipped_accounts.append(username)
                continue

            # Generate email and password
            email = f"{username}@university.edu"
            temp_password = generate_temporary_password()

            try:
                # Create User account
                new_user = User(
                    username=username,
                    email=email,
                    user_type='advisor'
                )
                new_user.set_password(temp_password)
                db.session.add(new_user)

                # Create Advisor record
                advisor_record = Advisor(
                    advisor_id=username,
                    department_id=advisor_info['department_id'],
                    phone=advisor_info['phone'],
                    office_location=advisor_info['office_location'],
                    office_hours='Mon-Fri 9:00-11:00',
                    max_students=50,
                    current_students=0
                )
                db.session.add(advisor_record)

                db.session.commit()

                created_accounts.append({
                    'username': username,
                    'temp_password': temp_password,
                    'email': email,
                    'department': advisor_info['department_id'],
                    'phone': advisor_info['phone'],
                    'office': advisor_info['office_location']
                })

                print(f"\nCreated account for advisor {username}")
                print(f"Department: {advisor_info['department_id']}")
                print(f"Office: {advisor_info['office_location']}")
                print(f"Phone: {advisor_info['phone']}")
                print("-" * 50)

            except Exception as e:
                print(f"Error creating account for advisor {username}: {str(e)}")
                db.session.rollback()

        # Generate report of created accounts
        if created_accounts:
            report_df = pd.DataFrame(created_accounts)
            report_df.to_excel('advisor_account_credentials.xlsx', index=False)
            print("\nTemporary credentials have been saved to 'advisor_account_credentials.xlsx'")

        print("\nAccount creation summary:")
        print(f"Created: {len(created_accounts)} accounts")
        print(f"Skipped: {len(skipped_accounts)} existing accounts")


def delete_all_advisors():
    app = create_app()

    with app.app_context():
        try:
            # Get all advisor usernames before deletion
            advisor_users = User.query.filter_by(user_type='advisor').all()
            advisor_usernames = [user.username for user in advisor_users]

            # Delete from User table
            deleted_users = User.query.filter_by(user_type='advisor').delete()

            # Delete from Advisor table
            deleted_advisors = Advisor.query.delete()

            # Commit the changes
            db.session.commit()

            print("\nDeleted Advisors:")
            for username in advisor_usernames:
                print(f"- {username}")

            print(f"\nDeletion Summary:")
            print(f"Deleted {deleted_users} user accounts")
            print(f"Deleted {deleted_advisors} advisor records")
            print("\nAll advisor data has been successfully deleted!")

        except Exception as e:
            db.session.rollback()
            print(f"Error during deletion: {str(e)}")


def verify_advisor_data_linkage():
    """Verify that all advisors have proper data linkage"""
    app = create_app()

    with app.app_context():
        all_advisors = Advisor.query.all()
        if not all_advisors:
            print("\nNo advisor records found in database.")
            return

        print("\nAdvisor Data Verification:")
        print("-" * 50)
        for advisor in all_advisors:
            user = User.query.filter_by(username=advisor.advisor_id).first()

            print(f"\nAdvisor {advisor.advisor_id}:")
            print(f"User account: {'Found' if user else 'Missing'}")
            print(f"Department: {advisor.department_id}")
            print(f"Office: {advisor.office_location}")
            print(f"Phone: {advisor.phone}")
            print(f"Office Hours: {advisor.office_hours}")
            print(f"Max Students: {advisor.max_students}")
            print(f"Current Students: {advisor.current_students}")


if __name__ == '__main__':
    excel_file = 'StudentsCourses.xlsx'  # Your existing Excel file

    while True:
        print("\nAdvisor Account Management")
        print("-" * 25)
        print("1. Create advisor accounts from data file")
        print("2. Verify advisor data linkage")
        print("3. Delete ALL advisor accounts")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ")

        if choice == '1':
            create_advisor_accounts(excel_file)
        elif choice == '2':
            verify_advisor_data_linkage()
        elif choice == '3':
            confirm = input("\nWARNING: This will delete ALL advisor accounts and data! Are you sure? (yes/no): ")
            if confirm.lower() == 'yes':
                delete_all_advisors()
            else:
                print("Deletion cancelled.")
        elif choice == '4':
            print("\nExiting program...")
            break
        else:
            print("Invalid choice! Please try again.")

        input("\nPress Enter to continue...")