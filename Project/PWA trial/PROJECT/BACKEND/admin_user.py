# admin_user.py
from application.data.models import User
from application.data.database import db

def create_admin_user():
    # Check if the admin user already exists
    admin_user = User.query.filter_by(is_admin =1).first()
    if not admin_user:
        # If the admin user does not exist, create one and assign the 'admin' role
        admin_user = User(
            username='admin',
            password='admin_password',  # Replace with a secure password
            email='admin@example.com',
            is_admin=1
            # Add other user attributes as needed
        )
        db.session.add(admin_user)
        db.session.commit()
