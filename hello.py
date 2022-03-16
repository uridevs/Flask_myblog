from flask import Flask, render_template

# Create a flask instance

app = Flask(__name__)


# Create a route decourator

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
    return render_template("user.html", name=name)


# Create custom error pages

# Invalid URL

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

