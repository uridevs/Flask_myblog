from email.policy import default
from enum import unique
from wsgiref.validate import validator
from flask import Flask, render_template, flash, request, redirect, url_for
from itsdangerous import exc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime, date
from wtforms.widgets import TextArea


# Create a flask instance
app = Flask(__name__)


#ADD database

# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Mysql DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:B47WpGyU@localhost/our_users'


# Secret KEY
app.config['SECRET_KEY'] = "MYSECRETKEY1234"

# Initialize the database

db = SQLAlchemy(app)
migrate = Migrate(app, db)



 # Create a Blog Post Model

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text())
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))


# Create a post form

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("submit")


@app.route('/posts')
def posts():
    # Get all the posts from database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)


@app.route('/posts/edit/<int:id>', methods=['GET','POST'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        # Update database
        db.session.add(post)
        db.session.commit()
        flash("POST has been Updated!")
        return redirect(url_for('post', id=post.id))
    
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)

    




@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, 
        content=form.content.data, 
        author=form.author.data,
        slug=form.slug.data)
        

        # Clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        # Add post data to database

        db.session.add(post)
        db.session.commit()

        flash("New Blog Post added succesfully!")

        # Redirect to the webpage

    return render_template("add_post.html", form=form)




#Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(80))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # passwords

    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a String
    def __repr__(self):
        return '< Name %r>' % self.name

# Create a Password test Class

class PasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password must match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Succesfully!")
        our_users = Users.query.order_by(Users.date_added)

        return render_template("add_user.html",
            form=form,
            name=name,
            our_users=our_users)

    except:
        flash("There was a problem trying to delete the user... Try again")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
            form=form,
            name=name,
            our_users=our_users
            )



@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']

        try:
            db.session.commit()
            flash("User Updated Succesfully")

            return render_template("update.html",
                form=form,
                name_to_update = name_to_update)

        except:
            flash("Error - Looks like there was some problem...")
            return render_template("update.html",
                form=form,
                name_to_update = name_to_update)
    
    our_users = Users.query.order_by(Users.date_added)
    return render_template("update.html",
                form=form,
                name_to_update = name_to_update,
                our_users=our_users)


@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hashing the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, 
                email=form.email.data, 
                favorite_color=form.favorite_color.data,
                password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data

        #Clear the form
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash("User Added Succesfully")

    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
        form=form,
        name=name,
        our_users=our_users)

# Create a route decorator
@app.route('/')
def index():
    first_name = "Javi"
    favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
    return render_template("index.html", 
    name=first_name,
    pizza=favorite_pizza
    
    )

@app.route('/user/<name>')
def user(name):
    return render_template("user.html",)


@app.route('/name', methods=['GET','POST'])
def name():
    name = None
    form = UserForm()

    # Validate Form
    if form.validate_on_submit():
        name = form.name.data

        #Clear the form
        form.name.data = ''
        flash("Form Submitted Succesfully")

    return render_template("name.html",
        name = name,
        form = form)

# Password test page 
@app.route('/test_pwd', methods=['GET','POST'])
def test_pwd():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        #Clear the form
        form.email.data = ''
        form.password_hash.data = ''
        #flash("Form Submitted Succesfully")

        #Look up user by email
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check hashed password

        passed = check_password_hash(pw_to_check.password_hash, password) 


    return render_template("test_pwd.html",
        email = email,
        password = password,
        pw_to_check = pw_to_check,
        passed = passed,
        form = form)

# Create custom error pages

# Invalid URL

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500




# Returning JSON

@app.route('/date')
def get_current_date():
    return {"Date": date.today()}

@app.route('/pizza')
def get_favourite_pizza():
    favorite_pizzas = {
        "Javi": "Bacon, cheese, beef, olives, onion",
        "Marti": "4 Quesos"
    }
    return favorite_pizzas
