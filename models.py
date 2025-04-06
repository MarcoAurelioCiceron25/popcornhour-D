
from extensions import db
from flask_login import UserMixin  # Import correcto para UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'  # Cambia el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    genre = db.Column(db.String(100))
    release_year = db.Column(db.Integer)
    moderator_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False) 
    comments = db.relationship("Comment", backref="movie", lazy=True)
    ratings = db.relationship("Rating", backref="movie", lazy=True)



class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id')) 

    # Relación con el modelo Usuario
    user = db.relationship("User", backref="rating", lazy=True) 


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  

    # Relación con el modelo Usuario
    user = db.relationship("User", backref="comments", lazy=True)

