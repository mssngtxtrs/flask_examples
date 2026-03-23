from datetime import timedelta

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy

from .admin.second import second

### SERVER CONFIGURATION

HOST = "127.0.0.1"
PORT = 5000

SECRET = "what"

SESSION_LIFETIME = timedelta(hours=12)

SQL_DATABASE_URI = "postgresql+psycopg://overlordhaha@127.0.0.1:5432/main"

### APP CONFIGURATION

app = Flask(__name__)
app.secret_key = SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = SQL_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = SESSION_LIFETIME

db = SQLAlchemy(app)

app.register_blueprint(second, url_prefix="/admin")


class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/view")
def view():
    all_users = users.query.all()
    return render_template("view.html", users=all_users)


@app.route("/page_<page>")
def page(page):
    foundPage = False
    for i in range(1, 100):
        if int(page) == i:
            foundPage = page

    if not foundPage:
        print(f"Failed loading page {page}")
        abort(404)
    else:
        return render_template("page.html", content=foundPage)


@app.route("/login", methods=["GET", "POST"])
def login():
    ### CHECKING FOR USED METHOD
    ## If POST, get username and store in session
    if request.method == "POST":
        user = request.form["username"]
        session["user"] = user

        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, None)
            db.session.add(usr)
            db.session.commit()

        flash("Logged in successfully.", "success")
        return redirect(url_for("user"))
    ## If GET, check if user is already logged in
    else:
        if "user" in session:
            flash("You are already logged in.", "info")
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/logout")
def logout():
    ## If user is logged in, log them out by removing from session
    session.pop("user", None)
    session.pop("email", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/account", methods=["GET", "POST"])
def user():
    email = None
    ## If user is logged in, show their account page
    if "user" in session:
        usr = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=usr).first()
            if found_user:
                found_user.email = email
                db.session.commit()
            flash("Email updated successfully.", "success")
            return redirect(url_for("user"))
        else:
            if "email" in session:
                email = session["email"]
            return render_template("user.html", usr=usr, email=email)
    else:
        return redirect(url_for("login"))


@app.errorhandler(404)
def not_found(error):
    print(f"Failed loading page: {error}")
    return render_template("404.html"), 404


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host=HOST, port=PORT)
