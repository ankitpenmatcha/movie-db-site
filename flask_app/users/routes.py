from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
import base64
from io import BytesIO
from .. import bcrypt
from werkzeug.utils import secure_filename
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdateProfilePicForm
from ..models import User

users = Blueprint("users", __name__)

""" ************ User Management views ************ """


# TODO: implement
@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('movies.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.save()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)


# TODO: implement
@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('movies.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('users.account'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)


# TODO: implement
@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('movies.index'))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    update_username_form = UpdateUsernameForm()
    update_profile_pic_form = UpdateProfilePicForm()
    if request.method == "POST":
        if update_username_form.submit_username.data and update_username_form.validate():
            current_user.username = update_username_form.username.data
            current_user.save()
            flash('Your username has been updated.', 'success')

        if update_profile_pic_form.submit_picture.data and update_profile_pic_form.validate():
            file = update_profile_pic_form.picture.data
            filename = secure_filename(file.filename)
            if filename != '':
                file_ext = '.' + filename.rsplit('.', 1)[1].lower()
                if file_ext not in ['.jpg', '.png', '.jpeg']:
                    flash('Invalid image format.', 'danger')
                else:
                    current_user.profile_pic.delete()
                    current_user.profile_pic.put(file, content_type=f'image/{file_ext.lstrip(".")}')
                    current_user.save()
                    flash('Your profile picture has been updated.', 'success')
                    
        return redirect(url_for('users.account'))

    # Logic for handling GET requests or the initial page load
    image_data = current_user.profile_pic
    return render_template('account.html', update_username_form=update_username_form, update_profile_pic_form=update_profile_pic_form, image=image_data)