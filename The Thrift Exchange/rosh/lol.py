from flask import Flask, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "triple9992foursix"

# --- File Helpers
def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
    with open("users.json", "r") as f:
        users = json.load(f)
    return users

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

# --- CSS
CSS = """
<style>
  body {
    font-family: Arial, sans-serif;
    text-align: center;
    margin: 0;
    padding: 0;
  }
  .container {
    margin-top: 100px;
    padding: 20px;
  }
  .card {
    margin: 20px;
    display: inline-block;
    width: 200px;
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    padding: 15px;
  }
  .card-title {
    font-size: 18px;
    font-weight: bold;
  }
  ul.list-group {
    list-style: none;
    padding: 0;
  }
  ul.list-group li {
    padding: 10px;
    border: 1px solid #ccc;
    margin: 5px 0;
    border-radius: 5px;
    background: white;
  }
  /* Base button */
  .button {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    font-family: Arial, sans-serif;
    cursor: pointer;
    margin: 5px;
    text-decoration: none;
    display: inline-block;
    transition: background-color 0.2s ease-in-out;
  }
  /* Button variations */
  .button-green {
    background-color: #28a745; color: white;
  }
  .button-green:hover { background-color: #218838; }
  .button-blue {
    background-color: #007bff; color: white;
  }
  .button-blue:hover { background-color: #0069d9; }
  .button-red {
    background-color: #dc3545; color: white;
  }
  .button-red:hover { background-color: #c82333; }
  .button-yellow {
    background-color: #ffc107; color: black;
  }
  .button-yellow:hover { background-color: #e0a800; }
</style>
"""

# --- Homepage
@app.route("/")
def homepage():
    return f"""
    <html>
    <head>
      <title>Thrift Exchange</title>
      {CSS}
    </head>
    <body style="background-color:#ECFAE5;">
      <div class="container">
        <h1 class="mb-3">Welcome to The Thrift Exchange!</h1>
        <p class="lead">Where preloved finds bring you joy. Sign up or login to start shopping!</p>
        <a href='/signup' class="button button-green">Sign Up</a>
        <a href='/login' class="button button-blue">Login</a>
      </div>
    </body>
    </html>
    """

# --- Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = load_users()
        if email in users:
            return f"""
            <html><head>{CSS}</head>
            <body style="background-color:#DDF6D2;">
              <div class="container">
                <h4>Email already exists. Try logging in.</h4>
                <a href='/login' class="button button-blue">Go to Login</a>
              </div>
            </body></html>
            """

        users[email] = {"password": password, "cart": {}}
        save_users(users)
        return f"""
        <html><head>{CSS}</head>
        <body style="background-color:#DDF6D2;">
          <div class="container">
            <h4>Signup successful!</h4>
            <a href='/login' class="button button-green">Login here</a>
          </div>
        </body>
        </html>
        """

    return f"""
    <html>
    <head>{CSS}</head>
    <body style="background-color:#DDF6D2;">
      <div class="container">
        <h2>Sign Up</h2>
        <form method="POST">
          <input type="text" name="email" placeholder="Email" required><br><br>
          <input type="password" name="password" placeholder="Password" required><br><br>
          <button type="submit" class="button button-green">Sign Up</button>
        </form>
        <a href='/' class="button button-blue">Back to Home</a>
      </div>
    </body>
    </html>
    """

# --- Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = load_users()
        if email not in users:
            return f"""
            <html><head>{CSS}</head>
            <body style="background-color:#CAE8BD;">
              <div class="container">
                <h4>Account couldn’t be found. Try registering.</h4>
                <a href='/signup' class="button button-green">Go to Sign Up</a>
              </div>
            </body></html>
            """
        if users[email]["password"] != password:
            return f"""
            <html><head>{CSS}</head>
            <body style="background-color:#CAE8BD;">
              <div class="container">
                <h4>Wrong password. Try again.</h4>
                <a href='/login' class="button button-blue">Back to Login</a>
              </div>
            </body></html>
            """

        session["email"] = email
        return redirect(url_for("items"))

    return f"""
    <html>
    <head>{CSS}</head>
    <body style="background-color:#CAE8BD;">
      <div class="container">
        <h2>Login</h2>
        <form method="POST">
          <input type="text" name="email" placeholder="Email" required><br><br>
          <input type="password" name="password" placeholder="Password" required><br><br>
          <button type="submit" class="button button-blue">Login</button>
        </form>
        <a href='/' class="button button-green">Back to Home</a>
      </div>
    </body>
    </html>
    """

# --- Items
@app.route("/items")
def items():
    if "email" not in session:
        return redirect(url_for("login"))

    return f"""
    <html>
    <head>{CSS}</head>
    <body style="background-color:#B0DB9C;">
      <div class="container">
        <h2>Shop Items</h2>
        <div class="row">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Shirt</h5>
              <p>RM10.00</p>
              <a href='/add/Shirt/10' class="button button-green">Add to Cart</a>
            </div>
          </div>
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Jeans</h5>
              <p>RM20.00</p>
              <a href='/add/Jeans/20' class="button button-green">Add to Cart</a>
            </div>
          </div>
        </div>
        <a href='/cart' class="button button-yellow">Go to Cart</a>
        <a href='/logout' class="button button-red">Logout</a>
      </div>
    </body>
    </html>
    """

# --- Add to Cart
@app.route("/add/<item>/<int:price>")
def add(item, price):
    if "email" not in session:
        return redirect(url_for("login"))

    users = load_users()
    email = session["email"]
    cart = users[email]["cart"]

    if item in cart:
        cart[item]["qty"] += 1
    else:
        cart[item] = {"qty": 1, "price": price}

    save_users(users)
    return redirect(url_for("cart"))

# --- Cart
@app.route("/cart")
def cart():
    if "email" not in session:
        return redirect(url_for("login"))

    users = load_users()
    email = session["email"]
    cart = users[email]["cart"]

    if not cart:
        return f"""
        <html><head>{CSS}</head>
        <body style="background-color:#ECFAE5;">
          <div class="container">
            <h3>Your cart is empty.</h3>
            <a href='/items' class="button button-green">Back to Shop</a>
          </div>
        </body></html>
        """

    cart_html = f"""
    <html>
    <head>{CSS}</head>
    <body style="background-color:#ECFAE5;">
      <div class="container">
        <h2>Your Cart</h2>
        <ul class="list-group">"""
    total = 0
    for item, details in cart.items():
        qty = details["qty"]
        price = details["price"]
        subtotal = qty * price
        total += subtotal
        cart_html += f"<li>{item} - RM{price} x {qty} = RM{subtotal} <a href='/remove/{item}' class='button button-red'>Remove</a></li>"
    cart_html += f"""
        </ul>
        <h3>Total: RM{total}</h3>
        <a href='/checkout' class="button button-green">Checkout</a>
        <a href='/items' class="button button-yellow">Back to Shop</a>
      </div>
    </body>
    </html>
    """
    return cart_html

# --- Remove Item
@app.route("/remove/<item>")
def remove(item):
    if "email" not in session:
        return redirect(url_for("login"))

    users = load_users()
    email = session["email"]
    cart = users[email]["cart"]

    if item in cart:
        if cart[item]["qty"] > 1:
            cart[item]["qty"] -= 1
        else:
            del cart[item]

    save_users(users)
    return redirect(url_for("cart"))

# --- Checkout
@app.route("/checkout")
def checkout():
    if "email" not in session:
        return redirect(url_for("login"))

    users = load_users()
    email = session["email"]
    cart = users[email]["cart"]

    total = sum(details["qty"] * details["price"] for details in cart.values())
    users[email]["cart"] = {}  # Clear cart after checkout
    save_users(users)

    return f"""
    <html><head>{CSS}</head>
    <body style="background-color:#ECFAE5;">
      <div class="container">
        <h3>Thank you for your purchase</h3>
        <p>Total amount: RM{total}</p>
        <p>Prepare your wallet to continue transaction.</p>
        <
        <a href='/items' class="button button-green">Continue Shopping</a>
      </div>
    </body>
    </html>
    """

# --- Logout
@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("homepage"))

# --- Run
if __name__ == "__main__":
    app.run(debug=True)

