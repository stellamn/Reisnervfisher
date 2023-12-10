import os

from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
db1 = SQL("sqlite:///timeline.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Show portfolio of stocks"""
    return render_template("index.html")


@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")


@app.route("/artifacts")
def artifacts():
    # Get transactions
    return render_template("artifacts.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Apologies, you must provide a usename")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Apologies, you must provide a password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/quiz")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/map", methods=["GET", "POST"])
def quote():
    return render_template("map.html")


@app.route("/timeline", methods=["POST", "GET"])
def timeline():
    if request.method == "POST":
        year = request.form.get("year")

        if not year:
            return apology("Apologies, you must enter a year")
        things = []
        data = db1.execute(
            "SELECT year, date, event, description FROM timeline WHERE year= :year",
            year=year,
        )
        if len(data) == 0:
            return apology("Apologies, there are no events for that year")
        for row in data:
            thing = {}
            thing["year"] = row["year"]
            thing["Date"] = row["Date"]
            thing["Event"] = row["Event"]
            thing["Description"] = row["Description"]
            things.append(thing)
        return render_template("timeline.html", things=things)
    else:
        return render_template("timeline.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Apologies, you must provide a usename")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Apologies, you must provide a password")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Apologies, you must confirm your password")

        # Ensure confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Apologies, your passwords do not match")

        password = request.form.get("password")
        username = request.form.get("username")
        hashed_password = generate_password_hash(password)

        count = db.execute(
            "SELECT COUNT(*) FROM users WHERE username = :username", username=username
        )[0]["COUNT(*)"]
        if count > 0:
            return apology("Apologies, this username already exists")
        else:
            db.execute(
                "INSERT INTO users (username, hash) VALUES(:username, :password)",
                username=username,
                password=hashed_password,
            )

        return redirect("/quiz")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/analysis", methods=["GET", "POST"])
def analysis():
    return render_template("analysis.html")


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    score = request.form.get("score")
    if score is not None:
        db.execute(
            "UPDATE users SET score=:score WHERE user_id = :user_id",
            {"user_id": session["user_id"], "score": score},
        )
        return render_template("quiz.html", score=score)
    else:
        return render_template("quiz.html")

