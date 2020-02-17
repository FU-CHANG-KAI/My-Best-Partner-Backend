import flask
from application import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Activity(db.Document):
    activity_id   = db.IntField( unique=True )
    activity_name = db.StringField( unique=True, max_length = 50 )
    leader_id     = db.IntField( required=True )
    leader_name   = db.StringField( max_length = 20)
    open_date     = db.DateTimeField( default=datetime.utcnow )
    start_date    = db.DateTimeField( )
    genre         = db.StringField( max_length = 20 )
    skills        = db.StringField( max_length = 50 )
    description   = db.StringField( max_length = 200 )

class User(db.Document):
    user_id       = db.IntField( unique=True )
    username      = db.StringField(max_length = 50)
    email         = db.StringField( max_length = 50 )
    password      = db.StringField( )
    sex           = db.StringField( max_length = 50 )
    hobbies       = db.StringField( max_length = 50 )
    skills        = db.StringField(max_length = 50 )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)

class Application(db.Document):
    apply_id      = db.IntField(  )
    applicant_id  = db.IntField( required=True )
    applicant_name= db.StringField( max_length = 50 )
    activity_id   = db.IntField( required=True )
    activity_name = db.StringField( max_length = 50 )
    status        = db.IntField( required=True, default=0 )