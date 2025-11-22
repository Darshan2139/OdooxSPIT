"""
StockMaster - Inventory Management System
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import string
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
# Load environment variables from .env file
password = "6969Ma@18082004"
encoded_password = quote_plus(password)
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{encoded_password}@localhost:5432/stockmaster"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])
db = SQLAlchemy(app)
# Initialize Flask-Mail
mail = Mail(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

def send_email(subject, sender, recipients, text_body, html_body=None):
    """Helper function to send emails"""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from models import User
        if not User.query.filter_by(email='admin@stockmaster.com').first():
            admin = User(
                name='Admin',
                email='admin@stockmaster.com',
                password=generate_password_hash('admin123'),
                role='inventory_manager'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin@stockmaster.com / admin123")

# Import routes after app is created
from routes import *

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

