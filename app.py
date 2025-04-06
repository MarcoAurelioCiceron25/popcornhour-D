from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from extensions import db # Importa db desde extensions
from models import User, Movie, Comment, Rating
from flask_migrate import Migrate
import bcrypt

# Configuración de Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.nlgzmcodzthkqetpghzv:iTkoJdHY5kU16PyG@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
app.config['SECRET_KEY'] = 'iTkoJdHY5kU16PyG'

# Inicializa SQLAlchemy con la aplicación Flask
db.init_app(app)

# Inicialización de extensiones
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inicialización de migraciones
migrate = Migrate(app, db)

# Importar modelos después de inicializar SQLAlchemy
from models import User, Movie

# Contexto para registrar tablas al inicio (solo si es necesario)
with app.app_context():
    db.create_all()  # Asegúrate de que las tablas existen

# Cargar el usuario con Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas para registro, login, etc.
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        raw_password = request.form['password']
        role = request.form['role']

        if role not in ["standard", "moderator"]:
            flash("Rol no válido", "error")
            return render_template('signup.html')

        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        user = User(username=username, email=email, password=hashed_password.decode('utf-8'), role=role)
        db.session.add(user)
        db.session.commit()

        flash("Registro exitoso. Por favor, inicia sesión.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        raw_password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(raw_password.encode("utf-8"), user.password.encode("utf-8")):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Email o contraseña incorrectos", "error")
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
     movies = Movie.query.all() # Muestra todas las películas
    
     return render_template('home.html', movies=movies)

@app.route('/')
@login_required
def index():
    return redirect(url_for('signup')) # Cambiar a plantilla

@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    if current_user.role != 'moderator':
        return render_template("error.html", error_message="Acceso no autorizado")
    if request.method == 'POST':
        title = request.form.get('title', "").strip()
        description = request.form.get('description', "").strip()
        genre = request.form.get('genre', "").strip()
        release_year = request.form.get('release_year', "").strip()

        if not title or not description or not genre or not release_year:
            return render_template("add_movie.html", error="Todos los campos son obligatorios")
        try:
            release_year = int(release_year)
        except ValueError:
            flash("El año debe ser un número válido", "error")
            return render_template("add_movie.html")

        movie = Movie(title=title, description=description, genre=genre, release_year=release_year, moderator_id=current_user.id)
        db.session.add(movie)
        db.session.commit()
        flash("Película agregada exitosamente", "success")
        return redirect(url_for('home'))
    return render_template("add_movie.html")

@app.route("/add_comment/<int:movie_id>", methods=["GET", "POST"])
@login_required
def add_comment(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == "POST":
        text = request.form.get("text", "").strip()

        if not text:
            flash("El comentario no puede estar vacio", "error")
            return redirect(url_for("add_comment", movie_id=movie_id))
        
        # Crear el comentario
        comment = Comment(text=text, movie_id=movie.id, user_id=current_user.id)  # Cambiado a usuario_id
        db.session.add(comment)
        db.session.commit()
        flash("Comentario agregado exitosamente", "success")
        return redirect(url_for("home", movie_id=movie_id))
    
    return render_template("add_comment.html", movie=movie)
    

@app.route('/add_rating/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def add_rating(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        score = request.form.get('score')

        try:
            score = int(score)
            if score < 1 or score > 10:  # Calificación de 1 a 10
                flash("El puntaje debe estar entre 1 y 10", "error")
                return redirect(url_for('add_rating', movie_id=movie_id))
        except ValueError:
            flash("El puntaje debe ser un número", "error")
            return redirect(url_for('home', movie_id=movie_id))

        # Crear el rating
        rating = Rating(score=score, movie_id=movie.id, user_id=current_user.id)
        db.session.add(rating)
        db.session.commit()
        flash("Calificación agregada exitosamente", "success")
        return redirect(url_for('movie_details', movie_id=movie_id))

    return render_template('add_rating.html', movie=movie)

@app.route("/movie/<int:movie_id>")
def movie_details(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    comments = Comment.query.filter_by(movie_id=movie.id).all()
    ratings = Rating.query.filter_by(movie_id=movie.id).all()
    return render_template("movie_details.html", movie=movie, comments=comments, ratings=ratings)
    
    return redirect(url_for("movie_details.html", movie_id=movie_id))



if __name__ == "__main__":
    app.run(debug=True)


