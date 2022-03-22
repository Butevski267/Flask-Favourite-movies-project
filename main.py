from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired
import requests
import sqlite3
from flask_sqlalchemy import SQLAlchemy

import requests

#_______________________________________________________________________________________________________________________
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##CREATE DATABASE_______________________________________________________________________________________________________
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top-10-movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False, unique=False)
    description = db.Column(db.String(250), nullable=False, unique=False)
    rating = db.Column(db.Float,nullable=True)
    ranking = db.Column(db.Integer, nullable=True, unique=False)
    review = db.Column(db.String(250), nullable=True, unique=False)
    img_url = db.Column(db.String(250), nullable=False, unique=False)


db.create_all()

title="Phone Booth"
year=2002
description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax."
rating=7.3
ranking=10
review="My favourite character was the caller."
img_url='https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg'

#new_movie = Movie(title=title,year=year,description=description,rating=rating,ranking=ranking,review=review,img_url=img_url)
#db.session.add(new_movie)
#db.session.commit()

#WTF_forms______________________________________________________________________________________________________________
class MovieForm(FlaskForm):
    rating = StringField('Your rating out of 10 e.g. 7.5')
    review = StringField('Your review')
    submit = SubmitField('Submit')

class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    add_button = SubmitField('Add Movie')


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
        db.session.commit()
    return render_template('index.html', movies=all_movies)

@app.route('/edit', methods=["GET","POST"])
def edit():
    form = MovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.review = form.review.data
        movie.rating = float(form.rating.data)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html',movie=movie, form=form)

@app.route('/delete')
def delete_movie():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/add', methods=['GET','POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        parameters = {
            'api_key': 'f3a6fd1ef9a760317db346e302f7d9c6',
            'query': movie_title,
        }
        response = requests.get(url='https://api.themoviedb.org/3/search/movie',
                                params=parameters)
        data = response.json()['results']
        return render_template('select.html', options=data)
    return render_template('add.html', form=form)

@app.route('/find')
def find():
    movie_id = request.args.get('id')
    img_url = 'https://image.tmdb.org/t/p/w500'
    if movie_id:

        parameters = {
            'api_key': 'f3a6fd1ef9a760317db346e302f7d9c6',
        }
        response = requests.get(url=f'https://api.themoviedb.org/3/movie/{movie_id}', params=parameters)
        data = response.json()
        print(data)
        new_movie = Movie(
            title = data['title'],
            year = data['release_date'].split('-')[0],
            img_url = f"{img_url}{data['poster_path']}",
            description = data["overview"],
            rating = 0.00,
            review = 'None'
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
