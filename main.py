from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm, EditProfileForm,ResetPasswordForm
from models import User, db
from dotenv import load_dotenv
import os
import random
import requests

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizusers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '123SAM456EEk789Sha0'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'profileImages')
csrf = CSRFProtect(app)
db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

DEFAULT_PROFILE_IMAGES = [
    'static/images/defaults/default1.jpg',  
    'static/images/defaults/default2.jpg',
    'static/images/defaults/default3.jpg',
]

# Home View
@app.route('/')
def home():
    return render_template("home.html")

# Registration View
@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email is already in use.', 'danger')
            return redirect(url_for('register'))
        if form.password.data != form.confirm_password.data:
            return redirect(url_for('register'))

        new_user = User(email=form.email.data, username=form.username.data, profile_image=None, score=0)
        new_user.set_password(form.password.data)

        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            form.profile_image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_user.profile_image = filename
        else:
            new_user.profile_image = random.choice(DEFAULT_PROFILE_IMAGES)

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=form)

# Login View
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid email or password.', 'danger')
    return render_template("login.html", form=form)

# Logout View
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Quiz View
@app.route("/quiz")
def quiz():
    category_id = request.args.get('category_id', 9)
    if category_id != 9 and not current_user.is_authenticated:
        flash("Login required to access Category Based Quiz", "danger")
        return redirect(url_for('login'))
    
    parameters = {"amount": 10, "category": category_id, "type": "multiple"}
    response = requests.get("https://opentdb.com/api.php", params=parameters)
    response.raise_for_status()
    question_data = response.json()["results"]

    for question in question_data:
        all_answers = question["incorrect_answers"] + [question["correct_answer"]]
        random.shuffle(all_answers)
        question["shuffled_answers"] = all_answers

    return render_template("Quiz.html", questions=question_data)

# User Profile View
@app.route("/userprofile", methods=["POST", "GET"])
@login_required
def userprofile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        if (current_user.username != form.username.data or 
            current_user.email != form.email.data or 
            not current_user.check_password(form.password.data)):
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('Your profile has been updated!', 'success')
        return redirect(url_for('userprofile'))
    return render_template("userprofile.html", user=current_user, form=form)

# Score Update View
@app.route('/update_score', methods=['POST'])
@login_required
def update_score():
    data = request.get_json()
    current_user.score += data.get('score', 0)
    db.session.commit()
    return jsonify({"status": "success", "new_score": current_user.score})

# Leaderboard View
@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.score.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('leaderboard.html', users=users)


@app.route("/resetPassword", methods=["POST", "GET"])
def resetPassword():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if not User.query.filter_by(email = form.email.data).first():
            flash("No Account found with this Email","danger")
            return redirect(url_for('resetPassword'))
        user = User.query.filter_by(email=form.email.data).first()
        user.set_password(form.new_password.data)
        db.session.commit()
        flash("Your Password is updated successfully","success")
        return redirect(url_for('resetPassword'))

    
    



    return render_template('resetPassword.html', form = form)



# Delete Account View
@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    db.session.delete(current_user)
    db.session.commit()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('register'))

if __name__ == "__main__":
    app.run(debug=True)
