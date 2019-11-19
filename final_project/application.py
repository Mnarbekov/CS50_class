import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
#export API_KEY=pk_5bc819ccdfdd4852ba8e332621f5dc12

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///visual_helper.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():

    rows = db.execute("SELECT * FROM projects WHERE user_id = :user_id", user_id=session["user_id"])

    if rows == []:
        return render_template("index_no.html")
    else:
        return render_template("index.html", projects=rows)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":

        # Ensure project name is provided
        if not request.form.get("name"):
            return apology("must provide name", 400)

        # Ensure audience is provided
        elif not request.form.get("audience"):
            return apology("must provide audience", 400)

        # Ensure summary is provided
        elif not request.form.get("summary"):
            return apology("must provide summary", 400)


        # If all good - proceed

        # Updated projects
        # Check if this share is not in the porfolio already - insert, else add
        db.execute("INSERT INTO projects (user_id, name, audience, summary, why, location, rating) VALUES (:user_id, :name, :audience, :summary, :why, :location, :rating)",
        user_id=session["user_id"], name=request.form.get("name"), audience=request.form.get("audience"), summary=request.form.get("summary"), why=request.form.get("why"),
        location=request.form.get("location"), rating=request.form.get("rating"))

        # All is good
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add.html")




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/top10", methods=["GET", "POST"])
@login_required
def top10():

    rows = db.execute("SELECT * FROM best_practices")

    return render_template("top10.html", practices=rows)


@app.route("/register", methods=["GET", "POST"])
def register():


    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure passwords match
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords should match", 400)


        #result = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))




        # Query database to add user

        result = db.execute("INSERT into users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))
        #rows = db.execute(("INSERT into users (username, hash) VALUES ('Misha', '123')")
        # hash_1=generate_password_hash(request.form.get("password")
        # Check if user exist
        if not result:
            return apology("username taken", 400)


        # Auto login new user
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        #return jsonify(True), 200
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")




@app.route("/del", methods=["GET", "POST"])
@login_required
def remove():

    # Creating list of symbols for sale
    names = db.execute("SELECT name FROM projects WHERE user_id = :user_id", user_id=session["user_id"])

    if names == []:
        return render_template("index_no.html")

    else:
        new_names=[]
        for name in names:
            new_names.append(name["name"])

        if request.method == "POST":

            # Ensure username was submitted
            #if not request.form.get("name"):
                #return apology("must provide name", 400)



            # All is good
            # Update portfolio
            # If shares selling less than on hand
            db.execute("DELETE FROM projects WHERE user_id = :user_id AND name = :name", user_id=session["user_id"], name=request.form.get("name"))


            return redirect("/")
        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("del.html", new_names=new_names)


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():

    # Creating list of projects
    names = db.execute("SELECT name FROM projects WHERE user_id = :user_id", user_id=session["user_id"])

    if names == []:
        return render_template("index_no.html")

    else:
        new_names=[]
        for name in names:
            new_names.append(name["name"])




        if request.method == "POST":


            # project name
            project = db.execute("SELECT * FROM projects WHERE name = :name", name = request.form.get("name"))
            return render_template("updated.html", project=project[0])

        else:
            return render_template("update.html", new_names=new_names)


@app.route("/updated", methods=["GET", "POST"])
@login_required
def updated():

    if request.method == "POST":

        db.execute("UPDATE projects SET audience = :audience, summary = :summary, why = :why, location = :location, rating = :rating WHERE name = :name", name = request.form.get("name"),
        audience=request.form.get("audience"), summary=request.form.get("summary"), why=request.form.get("why"), location=request.form.get("location"), rating=request.form.get("rating"))

        return redirect("/")
    else:
        return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
