import base64,io
from io import BytesIO
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import movie_client
from ..forms import MovieReviewForm, SearchForm
from ..models import User, Review
from ..utils import current_time

from datetime import datetime

movies = Blueprint("movies", __name__)
""" ************ Helper for pictures uses username to get their profile picture************ """
def get_b64_img(username):
    user = User.objects(username=username).first()
    
    if not user or not user.profile_pic:
        return None
    else:

    # Assuming user.profile_pic is a base64 string, decode it to bytes
        pic_bytes = base64.b64decode(user.profile_pic)

    # Create a BytesIO object with the decoded bytes
        bytes_im = io.BytesIO(pic_bytes)

    # If you need to further process the image or directly convert it to a base64 string for HTML embedding:
        base64_encoded_result = base64.b64encode(bytes_im.read()).decode('utf-8')

        return base64_encoded_result

""" ************ View functions ************ """


@movies.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("movies.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)


@movies.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = movie_client.search(query)
    except ValueError as e:
        return render_template("query.html", error_msg=str(e))

    return render_template("query.html", results=results)


@movies.route("/movies/<movie_id>", methods=["GET", "POST"])
def movie_detail(movie_id):
    try:
        result = movie_client.retrieve_movie_by_id(movie_id)
    except ValueError as e:
        return render_template("movie_detail.html", error_msg=str(e))

    form = MovieReviewForm()
    if form.validate_on_submit():
        review = Review (
            commenter=current_user,
            content=form.text.data,
            date=datetime.now(),
            imdb_id=movie_id,
            movie_title=result.title,
        )

        review.save()

        return redirect(request.path)

    reviews = Review.objects(imdb_id=movie_id)

    return render_template(
        "movie_detail.html", form=form, movie=result, reviews=reviews
    )


@movies.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    if not user:
        flash("User not found.", "warning")
        return redirect(url_for("movies.index"))  

    img = None
    if user.profile_pic: 
        img = get_b64_img(user.username)
        
    reviews = Review.objects(commenter=current_user)
 
    return render_template("user_detail.html", user=user, reviews=reviews, image=img)
