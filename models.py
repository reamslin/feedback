from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """connect to database"""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.VARCHAR(20), unique=True, nullable=False)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.VARCHAR(50), nullable=False, unique=True)

    first_name = db.Column(db.VARCHAR(30), nullable=False)

    last_name = db.Column(db.VARCHAR(30), nullable=False)

    @classmethod 
    def register(cls, username, password, email, first_name, last_name):

        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode('utf8')

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, password):
        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u 
        else:
            return False
    

class Feedback(db.Model):
    """feedback model"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.VARCHAR(100), nullable=False)

    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', backref='feedback')