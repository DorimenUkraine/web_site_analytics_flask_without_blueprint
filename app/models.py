from app import db, login_manager
from datetime import datetime
from flask_login import (LoginManager, UserMixin, login_required,
                         login_user, current_user, logout_user)
from werkzeug.security import generate_password_hash, check_password_hash


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    sr = db.relationship('Sites', backref='users', uselist=False)

    def __repr__(self):
        return f"<users {self.id}, {self.email}>"

    def set_password(self, password):
        self.psw = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.psw, password)


class Sites(db.Model):
    __tablename__ = 'sites'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(50), unique=True)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    vr = db.relationship('Visits', backref='sites', uselist=False)
    # br = db.relationship('Events', backref='sites', uselist=False)

    def __repr__(self):
        return f"<sites {self.id}, {self.url}>"


class ModelMixin(object):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Calendars(db.Model, ModelMixin):
    """Date record."""
    __tablename__ = 'calendars'
    datetime = db.Column(db.DateTime, primary_key=True)


class Visits(db.Model, ModelMixin):
    """Page visit record."""
    __tablename__ = 'visits'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(39))
    cid = db.Column(db.String(10))
    session = db.Column(db.String(10))
    datetime = db.Column(db.DateTime)
    doc_title = db.Column(db.Text)
    doc_uri = db.Column(db.Text)
    doc_enc = db.Column(db.String(25))
    referrer = db.Column(db.Text)
    _referrer = db.Column(db.Text)
    platform = db.Column(db.String(25))
    browser = db.Column(db.String(25))
    version = db.Column(db.String(25))
    screen_res = db.Column(db.String(25))
    screen_depth = db.Column(db.String(10))
    continent = db.Column(db.String(3))
    country = db.Column(db.String(3))
    subdivision_1 = db.Column(db.String(75))
    subdivision_2 = db.Column(db.String(75))
    city = db.Column(db.String(75))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    accuracy_radius = db.Column(db.Integer)
    time_zone = db.Column(db.String(50))
    lang = db.Column(db.String(10))
    _lang = db.Column(db.String(10))
    name = db.Column(db.Text)
    value = db.Column(db.Text)
    target = db.Column(db.Boolean, default=False)

    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))


# class Events(db.Model, ModelMixin):
#     """Interaction event record."""
#     __tablename__ = 'events'
#     id = db.Column(db.Integer, primary_key=True)
#     ip = db.Column(db.String(39))
#     cid = db.Column(db.String(10))
#     datetime = db.Column(db.DateTime)
#     doc_title = db.Column(db.Text)
#     doc_uri = db.Column(db.Text)
#     doc_enc = db.Column(db.String(25))
#     referrer = db.Column(db.Text)
#     _referrer = db.Column(db.Text)
#     platform = db.Column(db.String(25))
#     browser = db.Column(db.String(25))
#     version = db.Column(db.String(25))
#     screen_res = db.Column(db.String(25))
#     screen_depth = db.Column(db.String(10))
#     continent = db.Column(db.String(3))
#     country = db.Column(db.String(3))
#     subdivision_1 = db.Column(db.String(75))
#     subdivision_2 = db.Column(db.String(75))
#     city = db.Column(db.String(75))
#     latitude = db.Column(db.Float)
#     longitude = db.Column(db.Float)
#     accuracy_radius = db.Column(db.Integer)
#     time_zone = db.Column(db.String(50))
#     lang = db.Column(db.String(10))
#     _lang = db.Column(db.String(10))
#     name = db.Column(db.Text)
#     value = db.Column(db.Text)
#
#     site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)