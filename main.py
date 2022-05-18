from flask import Flask
from flask import render_template, redirect, url_for, flash
from flask import request
from flask_sqlalchemy import SQLAlchemy
import product

app = Flask(__name__)
app.config['SECRET_KEY'] = 'red_hot_chili_peppers'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    price = db.Column(db.Float, unique=True)
    qty = db.Column(db.Integer, default=0)


class Locations(db.Model):
    id = db.Column(db.Integer, primary_key=True)


@app.route('/')
def main():
    return render_template("home.html")


if __name__ == '__main__':
    app.run()
