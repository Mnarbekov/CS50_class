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
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    pf_rows = db.execute("SELECT * FROM portfolios WHERE user_id = :user_id", user_id=session["user_id"])

    if pf_rows == []:
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        cash = rows[0]['cash']
        return render_template("index.html", current_cash=usd(cash), total_cash=usd(cash))
    else:
        new_pf_rows = []
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        cash = rows[0]['cash']
        total_cash = cash

        for row in pf_rows:
            new_pf_dic = {}
            quote = lookup(row["symbol"])
            new_pf_dic["symbol"] = quote["symbol"]
            new_pf_dic["name"] = quote["name"]
            new_pf_dic["price"] = usd(quote["price"])
            new_pf_dic["shares"] = row["shares"]
            new_pf_dic["total"] = usd(row["shares"]*quote["price"])
            total_cash += row["shares"]*quote["price"]
            new_pf_rows.append(new_pf_dic)



        return render_template("index.html", new_pf_rows=new_pf_rows, current_cash=usd(cash), total_cash=usd(total_cash))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure password was submitted
        elif not request.form.get("shares"):
            return apology("must provide shares", 400)

        # Check that share is number
        elif not request.form.get("shares").isdigit():
            return apology("invalid shares", 400)

        # Check that share is integer
        elif not float(request.form.get("shares")).is_integer():
            return apology("invalid shares", 400)

        # Checking symbol using lookup
        shares = int(request.form.get("shares"))
        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)
        if quote == None:
            return apology("invalid symbol", 400)
        price = float(quote["price"])


        # Check that have enough cash
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        if rows[0]['cash'] < price*shares:
            return apology("can't afford", 400)

        # If all good - proceed
        # Decrease cash
        updated_cash = rows[0]['cash'] - price*shares
        db.execute("UPDATE users SET cash = :updated_cash WHERE id = :id", updated_cash=updated_cash, id=session["user_id"])

        # Updated portfolios table
        # Check if this share is not in the porfolio already - insert, else add
        rows = db.execute("SELECT * FROM portfolios WHERE user_id = :user_id AND symbol = :symbol", user_id=session["user_id"], symbol=symbol)
        if len(rows) == 0:
            db.execute("INSERT INTO portfolios (user_id, symbol, shares) VALUES (:user_id, :symbol, :shares)", user_id=session["user_id"], symbol=symbol, shares=shares)
        else:
            db.execute("UPDATE portfolios SET shares = shares + :shares WHERE user_id = :user_id AND symbol = :symbol", shares=shares, user_id=session["user_id"], symbol=symbol)

        # Update history table
        db.execute("INSERT INTO history (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)", user_id=session["user_id"], symbol=symbol, shares=shares, price=price)

        # All is good
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    rows = db.execute("SELECT username FROM users WHERE username = :username", username=username)
    if len(username) > 0 and len(rows) == 0:
        return jsonify(True), 200
    else:
        return jsonify(False), 200



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    rows = db.execute("SELECT * FROM history WHERE user_id = :user_id", user_id=session["user_id"])

    return render_template("history.html", history_list = rows)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    if request.method == "POST":
        # Ensure symbols were submitted
        if not request.form.get("symbol"):
            return apology("missing symbol", 400)

        # Checking symbol using lookup
        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)
        if quote == None:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", name=quote["name"], symbol=quote["symbol"], price=usd(quote["price"]))

    else:
        return render_template("quote.html")


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




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    # Creating list of symbols for sale
    symbols = db.execute("SELECT symbol FROM portfolios WHERE user_id = :user_id", user_id=session["user_id"])
    new_symbols=[]
    for symbol in symbols:
        new_symbols.append(symbol["symbol"])

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure password was submitted
        elif not request.form.get("shares"):
            return apology("must provide shares", 400)

        # Check that share is number
        elif not request.form.get("shares").isdigit():
            return apology("invalid shares", 400)

        # Check that share is integer
        elif not float(request.form.get("shares")).is_integer():
            return apology("invalid shares", 400)

        # Checking symbol using lookup
        shares = int(request.form.get("shares"))
        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)
        price = float(quote["price"])
        if quote == None:
            return apology("invalid symbol", 400)



        # If all good - proceed
        # Updated portfolios table
        # Check if this share is not in the porfolio already - insert, else add
        rows = db.execute("SELECT * FROM portfolios WHERE user_id = :user_id AND symbol = :symbol", user_id=session["user_id"], symbol=symbol)
        if len(rows) == 0:
            return apology("symbol not owned", 400)
        elif shares > rows[0]['shares']:
            return apology("too many shares", 400)

        # All is good
        # Update portfolio
        # If shares selling less than on hand
        if shares < rows[0]['shares']:
            db.execute("UPDATE portfolios SET shares = shares - :shares WHERE user_id = :user_id AND symbol = :symbol", shares=shares, user_id=session["user_id"], symbol=symbol)
        # If shares selling = on hands
        else:
            db.execute("DELETE FROM portfolios WHERE user_id = :user_id AND symbol = :symbol", user_id=session["user_id"], symbol=symbol)

        # Update history table
        db.execute("INSERT INTO history (user_id, symbol, shares, price) VALUES (:user_id, :symbol, -:shares, :price)", user_id=session["user_id"], symbol=symbol, shares=shares, price=price)
        # Add cash

        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        updated_cash = rows[0]['cash'] + price*shares
        db.execute("UPDATE users SET cash = :updated_cash WHERE id = :id", updated_cash=updated_cash, id=session["user_id"])


        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html", new_symbols=new_symbols)



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
