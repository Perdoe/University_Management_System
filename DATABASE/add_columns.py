from flask import Flask
from models.models import db
from config.config import Config
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.session.execute(text('ALTER TABLE instructor_courses ADD COLUMN IF NOT EXISTS time VARCHAR(50)'))
    db.session.execute(text('ALTER TABLE instructor_courses ADD COLUMN IF NOT EXISTS location VARCHAR(50)'))
    db.session.commit()
    print("Added columns!")