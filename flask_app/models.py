from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager


# TODO: implement
@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

# TODO: implement fields
class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True, min_length=1, max_length=40)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()

    def get_id(self):
        return self.username


# TODO: implement fields
class Review(db.Document):
    commenter = db.ReferenceField('User', required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.DateTimeField(default=datetime)
    imdb_id = db.StringField(required=True, length=9)
    movie_title = db.StringField(required=True, min_length=1, max_length=100)
    image = db.ImageField()