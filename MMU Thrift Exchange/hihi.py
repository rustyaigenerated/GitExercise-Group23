from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, random, smtplib, re, dns.resolver, uuid, os
from email.mime.text import MIMEText 
from datetime import datetime 
import dns.resolver
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/item_pics" 

app = Flask(__name__)
app.secret_key = "triple9992foursix"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


ADMINS = ["roshinyy_malar@yahoo.com"]

SMTP_EMAIL = "roshinimalar15@gmail.com"
SMTP_PASS = "fxyn yvhe fynq yfcq"

print(dns.__version__)  

# Helpers

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def send_verification_email(to_email, code):
    msg = MIMEText(f"Your MMU Thrift Exchange verification code is: {code}")
    msg["Subject"] = "Verification Code"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASS)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        print ("Email sent successfully.")
    except Exception as e:
        print("Email sending error:", e)
        return False

def is_valid_email_format(email):
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(regex, email) is not None

def domain_exists(email):
    domain = email.split("@")[-1]
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False

def load_items():
    try:
        with open("items.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_items(items):
    with open("items.json", "w") as f:
        json.dump(items, f, indent=4) 

def load_orders():
    try:
        with open("orders.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_orders(orders):
    with open("orders.json", "w") as f:
        json.dump(orders, f, indent=4)


def load_chats():
    try:
        with open("messages.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_chats(chats):
    with open("messages.json", "w") as f:
        json.dump(chats, f, indent=4)

def create_chat(buyer, seller):
    chats = load_chats()
    for cid, chat in chats.items():
        if chat["buyer"] == buyer and chat["seller"] == seller:
            return cid  
    
    chat_id = str(len(chats) + 1)
    chats[chat_id] = {
        "buyer": buyer,
        "seller": seller,
        "messages": [],
        "admin_joined": False
    }
    save_chats(chats)
    return chat_id

def add_chat_message(chat_id, sender, text):
    chats = load_chats()
    if chat_id not in chats:
        return False
    chats[chat_id]["messages"].append({
        "sender": sender,
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")

    })
    save_chats(chats)
    return True


def load_transactions():
    try:
        with open("transactions.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_transactions(transactions):
    with open("transactions.json", "w") as f:
        json.dump(transactions, f, indent=4)


def send_item_status_email(to_email, item_name, status):
    msg = MIMEText(f"Your item '{item_name}' has been {status} by the admin.")
    msg["Subject"] = f"Item {status.capitalize()} - MMU Thrift Exchange"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server: 
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASS)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print("Email sending error:", e)
        return False

def get_name(email):
    users = load_users()
    profile = users.get(email, {}).get("profile", {})
    full_name = f"{profile.get('first_name','')} {profile.get('last_name','')}".strip()
    return full_name if full_name else email


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]

        if not is_valid_email_format(email):
            flash("Enter a valid email address.", "error")
            return redirect(url_for("signup"))

        if not domain_exists(email):
            flash("Email domain does not exist. Use an existing email.", "error")
            return redirect(url_for("signup")) 

        users = load_users()
        if email in users:
            flash("Email already registered!", "error")
            return redirect(url_for("signup"))
        
        code = str(random.randint(1000, 9999))

        users[email] = {
            "password": password,
            "phone": phone,
            "verified": False,
            "verification_code": code,
            "profile": {
                "account_type": "user"
            }
        }
        save_users(users)     
    
        if send_verification_email(email, code):
            session["pending_user"] = email
            flash("Verification code sent to your email.", "success")
            return redirect(url_for("verify"))
        else:
            flash("Failed to send verification email. Please try again.", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if "pending_user" not in session:
        return redirect(url_for("signup"))

    email = session["pending_user"]
    users = load_users()

    if request.method == "POST":
        code_entered = request.form["code"]
        if users[email]["verification_code"] == code_entered:
            users[email]["verified"] = True
            users[email].pop("verification_code", None)  
            session.pop("pending_user", None)
            return redirect(url_for("login"))
        else:
            flash("Invalid code. Please try again.", "error")

    return render_template("verification.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = load_users() 
        if email in users and users[email]["password"] == password:
            if not users[email].get("verified", False):
                session["pending_user"] = email
                return redirect(url_for("verify"))

            session["user"] = email
            session["is_admin"] = email in ADMINS
            if session["is_admin"]:
                session["role"] = "admin"
            else:
                session["role"] = users[email].get("profile", {}).get("account_type", "buyer")
            session["email"] = email 
            return redirect(url_for("profile"))
        else:
            flash("Invalid login credentials", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    users = load_users()
    email = session["user"]
    edit_mode = request.args.get("edit") == "1"
    is_admin = email in ADMINS

    if request.method == "POST":
        gender = request.form["gender"]

        if is_admin:
            account_type = "admin" 
        else:
            account_type = request.form.get("account_type", users[email]["profile"].get("account_type", "buyer"))

        profile_data = {
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "age": request.form["age"],
            "gender": gender,
            "faculty": request.form["faculty"],
            "phone": request.form["phone"],
            "account_type": account_type,
            "profile_pic": "Male.png" if gender == 'Male' else "Female.png"
        }
        users[email]["profile"] = profile_data
        save_users(users)

        session["role"] = account_type
        flash("Profile updated successfully", "success")

        if is_admin: 
            return redirect(url_for("admin_dashboard")) 
        else:
            return redirect(url_for("profile")) 
    
    profile_data = users[email].get("profile", {})
    return render_template("profile.html", profile=profile_data, edit_mode=edit_mode, is_admin=is_admin)

@app.route("/profile/<email>")
def view_profile(email):
    users = load_users()
    profile = users.get(email, {}).get("profile", {})
    if not profile:
        return redirect(url_for("items"))

    return render_template("view_profile.html", profile=profile, email=email)


@app.route("/upload_item", methods=["GET", "POST"])
def upload_item():
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"]

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]
        category = request.form["category"]

        image_file = request.files["image"]
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)

        items = load_items()

        prefix_map = {
            "Clothes": "C",
            "Shoes": "S",
            "Accessories": "A",
            "Others": "O"
        }
        prefix = prefix_map.get(category, "O")
        count = sum(1 for i in items.values() if i.get("category") == category)
        item_code = f"{prefix}{count+1:03d}"  

        upload_date = datetime.now().strftime("%A, %d %B %Y")

       
        items[item_code] = {
           "image": filename,
           "name": name,
           "seller": email,
           "description": description,
           "price": float(price),
           "status": "pending",
           "category": category,
           "item_code": item_code,   
           "upload_date": upload_date
        }

        save_items(items)

        flash("Item uploaded successfully! Awaiting admin approval.", "success")
        return redirect(url_for("items"))

    return render_template("upload_item.html")






