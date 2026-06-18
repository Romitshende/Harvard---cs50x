import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
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


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # 1. Query the database for the user's active holdings
    # We aggregate shares using SUM and use 'HAVING total_shares > 0' to filter out stocks they completely sold off.
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0",
        session["user_id"]
    )

    # 2. Grab the user's remaining liquid cash balance
    user_data = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    user_cash = user_data[0]["cash"]

    # Start our grand total calculation with liquid cash
    grand_total = user_cash

    # 3. Inject real-time market values into our data dictionary
    for stock in stocks:
        live_data = lookup(stock["symbol"])
        stock["name"] = live_data["name"]
        stock["price"] = live_data["price"]
        stock["total_val"] = live_data["price"] * stock["total_shares"]

        # Add the value of this stock holding to our portfolio grand total
        grand_total += stock["total_val"]

    # 4. Pass our structured assets to the homepage dashboard template
    return render_template("index.html", stocks=stocks, cash=user_cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_input = request.form.get("shares")

        # 1. Ensure symbol was submitted
        if not symbol:
            return apology("must provide stock symbol", 400)

        # 2. Look up the stock using the API helper
        stock = lookup(symbol)
        if not stock:
            return apology("invalid stock symbol", 400)

        # 3. Ensure shares input is a positive whole integer
        # .isdigit() checks if the string contains only numbers (rejects negatives, decimals, and text)
        if not shares_input or not shares_input.isdigit():
            return apology("shares must be a positive integer", 400)

        shares = int(shares_input)
        if shares <= 0:
            return apology("shares must be greater than 0", 400)

        # 4. Calculate total cost and check user's current cash balance
        total_cost = stock["price"] * shares
        user_data = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        user_cash = user_data[0]["cash"]

        # 5. Check if user can afford it
        if user_cash < total_cost:
            return apology("can't afford transaction total", 400)

        # 6. Deduct cash from user's account balance
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, session["user_id"])

        # 7. Record the transaction in your tracking table
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"], stock["symbol"], shares, stock["price"]
        )

        # Flash a green success notification message
        flash("Bought successfully!")

        # Redirect user to home page
        return redirect("/")

    else:
        # If user just visits the route, show them the buy form
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Query your tracking database table for ALL transactions matching this user ID
    # Sorting by 'timestamp DESC' ensures their newest trades show up at the top of the log
    transactions = db.execute(
        "SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC",
        session["user_id"]
    )

    # Render the history template, passing the raw transaction lists through
    return render_template("history.html", transactions=transactions)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # 1. Ensure the user actually typed a symbol
        if not symbol:
            return apology("must provide stock symbol", 400)

        # 2. Call the provided lookup helper function to fetch live API data
        # 'stock' will be a dictionary containing {"name": "...", "price": ..., "symbol": "..."}
        stock = lookup(symbol)

        # 3. If the ticker symbol doesn't exist, lookup returns None
        if not stock:
            return apology("invalid stock symbol", 400)

        # 4. Pass the live stock dictionary straight to your results template
        return render_template("quoted.html", stock=stock)

    else:
        # If they just navigated to the page, show them the search form
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # 1. Require username, password, and confirmation matching
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)

        # 2. Query database to check if username already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("username already taken", 400)

        # 3. Hash the password safely and insert into the users table
        hashed_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_password)

        # 4. Automatically log the user in by saving their new ID to the session
        new_user = db.execute("SELECT id FROM users WHERE username = ?", username)
        session["user_id"] = new_user[0]["id"]

        # Redirect to the homepage portfolio
        return redirect("/")

    else:
        # If user clicks a link to get here, just show them the signup form
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # 1. Grab all stocks the current user owns so we can populate a dropdown selection menu
    owned_stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0",
        session["user_id"]
    )

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_input = request.form.get("shares")

        # 2. Form input validation checks
        if not symbol:
            return apology("must select a stock symbol", 400)

        if not shares_input or not shares_input.isdigit():
            return apology("shares must be a positive integer", 400)

        shares_to_sell = int(shares_input)
        if shares_to_sell <= 0:
            return apology("shares must be greater than 0", 400)

        # 3. Cross-reference to make sure they actually own enough shares of that specific stock
        user_shares = 0
        for stock in owned_stocks:
            if stock["symbol"] == symbol:
                user_shares = stock["total_shares"]

        if shares_to_sell > user_shares:
            return apology("you do not own that many shares", 400)

        # 4. Fetch the live market price to compute the payout credit
        stock = lookup(symbol)
        credit_value = stock["price"] * shares_to_sell

        # 5. Add the money back to the user's cash pool
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?",
                   credit_value, session["user_id"])

        # 6. Log the transaction using a NEGATIVE integer value for the shares column
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"], stock["symbol"], -shares_to_sell, stock["price"]
        )

        flash("Sold successfully!")
        return redirect("/")

    else:
        # Pass the user's active holdings down to the form so the dropdown can load them dynamically
        return render_template("sell.html", stocks=owned_stocks)


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Allow user to deposit additional simulated cash"""
    if request.method == "POST":
        amount_input = request.form.get("amount")

        # 1. Validate that the input exists and is a positive integer
        if not amount_input or not amount_input.isdigit():
            return apology("must provide a valid positive amount", 400)

        amount = int(amount_input)
        if amount <= 0:
            return apology("amount must be greater than 0", 400)

        # Optional: Set a reasonable maximum deposit limit (e.g., $100,000)
        if amount > 100000:
            return apology("maximum deposit limit is $100,000 at a time", 400)

        # 2. Update the user's cash balance in the database
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amount, session["user_id"])

        # Flash a green success message
        flash(f"Successfully deposited {usd(amount)}!")
        return redirect("/")

    else:
        return render_template("add_cash.html")
