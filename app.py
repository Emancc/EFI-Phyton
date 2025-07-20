from flask import Flask, render_template,url_for,flash,redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_required, login_user, logout_user


app = Flask(__name__)
app.secret_key = 'mi_super_secreto_12345' 

# Configuración de MySQL (ajusta los valores)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_blogs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'
from models import Users, Blogs

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def index():
    blogs = Blogs.query.all()  # Trae todos los blogs desde la BD
    return render_template('index.html', blogs=blogs)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/crear_blog', methods=['GET', 'POST'])
@login_required
def crear_blog():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']

        nuevo_blog = Blogs(title=titulo, description=descripcion, user_id=current_user.id)

        db.session.add(nuevo_blog)
        db.session.commit()

        flash('Blog creado con éxito', 'success')
        return redirect(url_for('index'))

    return render_template('crear_blog.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user_exist = Users.query.filter((Users.username == username) | (Users.email == email)).first()
        if user_exist:
            flash('El usuario o email ya existe', 'danger')
            return redirect(url_for('register'))

        new_user = Users(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso, ya puedes iniciar sesión', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Has iniciado sesión correctamente', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))

    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

@app.route('/like/<int:blog_id>', methods=['POST'])
def like(blog_id):
    blog = Blogs.query.get_or_404(blog_id)
    blog.likes += 1
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:blog_id>', methods=['POST'])
def delete(blog_id):
    blog = Blogs.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:blog_id>', methods=['GET', 'POST'])
def edit(blog_id):
    blog = Blogs.query.get_or_404(blog_id)
    if request.method == 'POST':
        blog.title = request.form['title']
        blog.description = request.form['description']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_blog.html', blog=blog)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
