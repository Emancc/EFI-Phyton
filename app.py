from flask import Flask,render_template, request, flash
from models import db, Blogs
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/crear_blog', methods=['POST', 'GET'])
#@login_required
def city():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']

        new_blog = Blogs(title=title, description=description)
        db.session.add(new_blog)
        db.session.commit()
        flash("Blog added succefully", "success")


    blog_list = Blogs.query.all()
    return render_template(
        'index.html',
        blogs=blog_list # nombre en html = nombre en back
    )
def crear_blog():
    return render_template('crear_blog.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/register')
def register():
    return render_template('auth/register.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
