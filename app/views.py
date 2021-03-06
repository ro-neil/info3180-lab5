"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm
from app.models import UserProfile
from werkzeug.security import check_password_hash


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


@app.route('/secure-page')
@login_required
def secure_page():
    """Render a page on our website that only logged in users can access."""
    return render_template('secure_page.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('secure_page'))

    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # Get the username and password values from the form.
            username = form.username.data
            password = form.password.data

            # query database for a user based on the username
            user = UserProfile.query.filter_by(username=username).first()
            # validate the password and ensure that a user was found
            if user is not None and check_password_hash(user.password, password):
                login_user(user)    # load into session
                flash('Logged in successfully.', 'success') # flash a message to the user
                return redirect(url_for("secure_page"))  # they should be redirected to a secure-page route instead
            else:
                flash('Username or Password is incorrect.', 'danger')
    flash_errors(form)
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    # Logs out the user and ends the session
    logout_user()
    flash('You have been logged out.', 'danger')
    return redirect(url_for('home'))


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))

# Flash errors from the form if validation fails with Flask-WTF
# http://flask.pocoo.org/snippets/12/
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text, error), 'danger')


###
# The functions below should be applicable to all Flask apps.
###


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
