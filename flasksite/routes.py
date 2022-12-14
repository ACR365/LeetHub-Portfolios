from flask import render_template, url_for, flash, redirect, request
# from flask_bcrypt import Bcrypt
from flasksite.forms import RegistrationForm, LoginForm, SearchForm, PostForm
# from flask_behind_proxy import FlaskBehindProxy
# from flask_sqlalchemy import SQLAlchemy
from flasksite.model import User,MyChart,circleChart
from flasksite import app, bcrypt, db, proxied, github
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse, urljoin
from leetcode import get_submissions_difficulty,get_submissions_date,get_submissions,get_submissions_level
from sqlalchemy import or_


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
  profiles = User.query.order_by(User.id.desc())
  return render_template('profiles.html', subtitle="Profiles", users=profiles)


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        print("Successful post")
        flash('Your post has been created!', 'success')
        return redirect(url_for("home"))
    else:
        # form.
        print(f"is submitted: {form.is_submitted()}")
        print("Unsuccessful post")
    return render_template("new_post.html", post_form=form)


@app.context_processor
def base():
  form = SearchForm()
  return dict(form=form)

@app.route("/search", methods=["POST"])
def search():
  form = SearchForm()
  if not form.validate_on_submit():
    return redirect(url_for('home'))
  else:
    search_query = form.searched.data
    user_obj = User.query.filter(or_(
      (User.username.like(f'%{search_query}%')), 
      (User.email.like(f'{search_query}%')),
      (User.school.like(f'{search_query}%')),
      (User.grad_year == f'{search_query}-01-01')
      )).all()

    return render_template("search.html", form=form, searched=search_query, users=user_obj)


@app.route("/register", methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  login_form = LoginForm()
  reg_form = RegistrationForm()
  if reg_form.validate_on_submit():
    user = User(username=reg_form.username.data, email=reg_form.email.data, school=reg_form.school.data, grad_year=reg_form.grad_year.data,password_hash=hash_pass(reg_form.password.data))
    db.session.add(user)
    db.session.commit()

    flash(f'Account created for {reg_form.username.data}!', 'success')
    return redirect(url_for('github_login'))
  return render_template('register.html', title='Register', login_form=login_form, register_form=reg_form)

@app.route('/github-login')
def github_login():
    return github.authorize()

@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    print("Running authorized()...")
    print(f'Token: {oauth_token}')
    next_url = request.args.get('next') or url_for('home')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=oauth_token).first()
    if user is None:
        user = User.query.order_by(User.id.desc()).first() # since user is created in register(), just retrieve latest entry 
        # db.session.add(user)

    user.github_access_token = oauth_token
    print(user)
    login_user(user)
    db.session.commit()
    return redirect(next_url), oauth_token

@app.route("/login", methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  # query the database to see if the username is present;
  # if so check for matching hash
  # if no username present reprompt;
  login_form = LoginForm()
  # reg_form = RegistrationForm()
  if login_form.validate_on_submit():
    given_user = login_form.existing_user.data # form inputs
    given_pass = login_form.existing_pass.data
    user_obj = User.query.filter_by(username=given_user).first()

    if (user_obj and bcrypt.check_password_hash(user_obj.password_hash, given_pass)):
      login_user(user_obj)        

      next = request.args.get('next')

      if not is_safe_url(next):
          return abort(400)

      flash(f'Successfully logged in as {login_form.existing_user.data}!', 'success')
      return redirect(next or url_for('home'))
    else:
      flash(f'Invalid username and/or password', 'danger')      
  return render_template('login.html', title="Login", login_form=login_form)


@app.route("/logout")
def logout():
  logout_user()
  return redirect(url_for('home'))


@app.route("/profile")
@login_required
def profile():
  profile_pic = url_for('static', filename=f"img/{current_user.profile_pic}")
  chart = MyChart()
  try:
    submissions = get_submissions_date(current_user.username)
  except:
    return render_template("profile.html", subtitle="Profile") 
  else: 
    if(len(submissions) < 3):
      display_graph = False
    else:
      display_graph = True
    labels = []
    values = []
    for date,val in submissions.items():
      labels.append(date)
      values.append(val)
    chart.labels.group = labels
    chart.data.submission.data = values
    NewChart = chart.get()
    sub = get_submissions_level(current_user.username)
    chart = circleChart()
    chart.data.submission.data = [sub['Easy'],sub['Medium'],sub['Hard']]
    cChart = chart.get()
    
    return render_template("profile.html", subtitle="Profile", chartJSON = NewChart,profile_pic=profile_pic,\
      display_graph= display_graph,submissions = get_submissions(current_user.username),\
        circleChartJSON=cChart, solved = sub["solved"])
  
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def hash_pass(password):
  pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
  return pw_hash

  