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


@app.route("/items")
def items():
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"]
    users = load_users()
    role = users[email].get("profile", {}).get("account_type", "buyer")
    all_items = load_items() 

    if role == "seller":
        seller_items = {k: v for k, v in all_items.items() if v["seller"] == email}
        return render_template("seller_items.html", items=seller_items, role="seller")
    else:
        approved_items = {k: v for k, v in all_items.items() if v["status"] == "approved"} 
        category = request.args.get("category")
        if category and category != "All":
            approved_items = {k: v for k, v in approved_items.items() if v["category"] == category} 
        for v in approved_items.values():
            v["seller_name"] = get_name(v["seller"])
        return render_template("buyer_items.html", items=approved_items, role="buyer")


@app.route("/admin/items")
def admin_items():
    if session.get("email") not in ADMINS:
        flash("Access denied")
        return redirect(url_for("index"))
    
    items = load_items()
    return render_template("admin_items.html", items=items)


@app.route("/add_to_cart/<item_id>")
def add_to_cart(item_id):
    if "user" not in session:
        flash("Login required to add items to cart", "error")
        return redirect(url_for("login"))

    email = session["user"]
    users = load_users()
    items = load_items()

    if item_id not in items or items[item_id]["status"] != "approved":
        flash("Item not available.", "error")
        return redirect(url_for("items"))

    if "cart" not in users[email]:
        users[email]["cart"] = {}

    if users[email]["cart"].get(item_id, 0) >= 1:
        if not session.get("out_of_stock_flash", False):
            flash("Item out of stock.", "error")
            session["out_of_stock_flash"] = True
        return redirect(url_for("items"))

    users[email]["cart"][item_id] = 1
    save_users(users)

    flash("Item added to cart!", "success")
    return redirect(url_for("items"))


@app.route("/remove_from_cart/<item_id>")
def remove_from_cart(item_id):
    if "user" not in session:
        flash("Login required.", "error")
        return redirect(url_for("login"))

    email = session["user"]
    users = load_users()

    if "cart" in users[email] and item_id in users[email]["cart"]:
        if users[email]["cart"][item_id] > 1:
            users[email]["cart"][item_id] -= 1
        else:
            del users[email]["cart"][item_id]

        save_users(users)
        flash("Item removed from cart.", "success")
    else:
        flash("Item not found in your cart.", "error")

    return redirect(url_for("cart"))


@app.route("/admin/approve/<item_id>")
def approve_item(item_id):
    items = load_items()
    if item_id in items:
        items[item_id]["status"] = "approved"
        save_items(items)

        # notify seller
        send_item_status_email(items[item_id]["seller"], items[item_id]["name"], "approved")
        flash(f"Item '{items[item_id]['name']}' approved and seller notified.", "success")
    return redirect(url_for("admin_items"))


@app.route("/admin/reject/<item_id>")
def reject_item(item_id):
    items = load_items()
    if item_id in items:
        seller_email = items[item_id]["seller"]
        item_name = items[item_id]["name"]

        # notify seller
        send_item_status_email(seller_email, item_name, "rejected")

        # delete item
        del items[item_id]
        save_items(items)
        flash(f"Item '{item_name}' rejected and seller notified.", "danger")
    return redirect(url_for("admin_items"))


@app.route("/cart")
def cart():
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"]
    users = load_users()
    items = load_items()
    cart_items = []
    total_price = 0

    if "cart" in users[email]:
        for item_id, qty in users[email]["cart"].items():
            if item_id in items:
                item = items[item_id]
                subtotal = item["price"] * qty
                total_price += subtotal
                cart_items.append({
                    "id": item_id,
                    "name": item["name"],
                    "price": item["price"],
                    "qty": qty,
                    "subtotal": subtotal
                })

    return render_template("cart.html", cart_items=cart_items, total=total_price)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user" not in session:
        return redirect(url_for("login"))

    current_user = session["user"]
    users = load_users() 
    cart = users[current_user].get("cart", {})
    
    if not cart:
        flash("Cart is empty.", "error")
        return redirect(url_for("cart"))

    if request.method == "POST":
        address = request.form["address"]
        delivery = request.form["delivery"]
        payment = request.form["payment"]

       
        orders = load_orders()
        order_id = str(len(orders) + 1)

        items = load_items()
        sellers = list({items[iid]["seller"] for iid in cart if iid in items})

        orders[order_id] = {
            "buyer": current_user,
            "sellers": sellers,
            "cart": {iid: qty for iid, qty in cart.items() if iid in items},  # only valid items
            "address": address,
            "delivery": delivery,
            "payment": payment,
            "status": "Pending",
            "buyer_confirmed": False,
            "seller_confirmed": False
        }
        save_orders(orders)

        
        users[current_user]["cart"] = {}
        save_users(users)

        flash("Order created. Contact seller(s) to proceed.", "success")
        return redirect(url_for("transactions"))

 
    return render_template("checkout.html")



@app.route("/confirm_payment/<order_id>", methods=["POST"])
def confirm_payment(order_id):
    if "user" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user_email = session["user"]
    orders = load_orders()

    if order_id not in orders:
        flash("Order not found.", "danger")
        return redirect(url_for("transactions"))

    order = orders[order_id]

   
    if user_email == order["buyer"] and not order.get("buyer_confirmed", False):
        order["buyer_confirmed"] = True
        flash("You have confirmed payment as Buyer.", "success")

    
    elif user_email in order.get("sellers", []) and not order.get("seller_confirmed", False):
        order["seller_confirmed"] = True
        flash("You have confirmed payment as Seller.", "success")

    else:
        flash("You have already confirmed or are not authorized.", "warning")

    
    if order.get("buyer_confirmed") and order.get("seller_confirmed"):
        order["status"] = "Completed"
        items = load_items()
        for iid in order.get("cart", {}).keys():
            if iid in items:
                items[iid]["status"] = "sold"
        save_items(items)
        flash("Order completed. Items marked as sold.", "success")

    with open("orders.json", "w") as f:
        json.dump(orders, f, indent=4)

    return redirect(url_for("transactions"))


@app.route("/admin/dashboard")
def admin_dashboard():
    if "user" not in session or not session.get("is_admin", False):
        return redirect(url_for("login"))

    items = load_items()
    orders = load_orders()
    users = load_users()

    order_list = []
    for oid, order in orders.items():
        buyer_profile = users.get(order["buyer"], {}).get("profile", {})
        buyer_name = f"{buyer_profile.get('first_name','')} {buyer_profile.get('last_name','')}".strip() or order["buyer"]
        buyer_phone = users.get(order["buyer"], {}).get("phone", "N/A")

        cart_details = []
        for iid, qty in order.get("cart", {}).items():
            item = items.get(iid)
            if item:
                cart_details.append(f"{item['name']} (x{qty})")
            else:
                cart_details.append(f"[Deleted Item {iid}] (x{qty})")

        order_list.append({
            "id": oid,
            "buyer": buyer_name,
            "buyer_phone": buyer_phone,
            "items": cart_details,
            "status": order["status"],
            "delivery": order["delivery"],
            "payment": order["payment"],
            "address": order["address"],
        })

    return render_template("admin_dashboard.html", items=items, orders=order_list)



@app.route("/admin/update_order/<order_id>/<status>")
def admin_update_order(order_id, status):
    if "user" not in session or not session.get("is_admin", False):
        return redirect(url_for("login"))

    orders = load_orders()
    if order_id in orders:
        orders[order_id]["status"] = status
        save_orders(orders) 

    return redirect(url_for("admin_dashboard"))


@app.route("/transactions")
def transactions():
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"]
    users = load_users()
    orders = load_orders()
    items = load_items()

    def get_name(email):
        profile = users.get(email, {}).get("profile", {})
        full_name = f"{profile.get('first_name','')} {profile.get('last_name','')}".strip()
        return full_name if full_name else email

    my_orders = []
    for oid, order in orders.items():
        if email == order["buyer"] or email in order.get("sellers", []):
            cart_details = []
            for iid, qty in order.get("cart", {}).items():
                item = items.get(iid)
                if item:
                    cart_details.append(f"{item['item_code']} - {item['name']} (x{qty})")
                else:
                    cart_details.append(f"[Deleted Item {iid}] (x{qty})")

            order_info = {
                "id": oid,
                "buyer": get_name(order["buyer"]),
                "cart": cart_details,
                "status": order["status"],
                "delivery": order["delivery"],
                "payment": order["payment"],
                "address": order["address"],
                "buyer_confirmed": order.get("buyer_confirmed", False),
                "seller_confirmed": order.get("seller_confirmed", False),
                "sellers": [get_name(s) for s in order.get("sellers", [])]
            }

            if email == order["buyer"]:
                order_info["contact"] = [users[s]["phone"] for s in order["sellers"] if s in users]
            else:
                order_info["contact"] = [users[order["buyer"]]["phone"]] if order["buyer"] in users else []

            my_orders.append(order_info)

    return render_template("transactions.html", transactions=my_orders)


@app.route("/start_chat/<seller_email>")
def start_chat(seller_email):
    buyer_email = session["user"]

    chat_id = create_chat(buyer_email, seller_email)

    return redirect(url_for("chat", chat_id=chat_id))


@app.route("/chat/<chat_id>", methods=["GET", "POST"])
def chat(chat_id):
    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]
    users = load_users()
    chats = load_chats()

    if chat_id not in chats:
        flash("Chat not found", "error")
        return redirect(url_for("inbox"))

    chat_data = chats[chat_id]

    if session.get("role") == "admin":
        chat_data["unread_for_admin"] = False
    else:
        if "unread_for" not in chat_data:
            chat_data["unread_for"] = {}
        chat_data["unread_for"][user] = False

    save_chats(chats) 

    def get_name(email):
        profile = users.get(email, {}).get("profile", {})
        full_name = f"{profile.get('first_name','')} {profile.get('last_name','')}".strip()
        return full_name if full_name else email

    buyer_name = get_name(chat_data["buyer"])
    seller_name = get_name(chat_data["seller"])

    if request.method == "POST":
        message = request.form["message"]
        add_chat_message(chat_id, user, message)
        return redirect(url_for("chat", chat_id=chat_id))

    return render_template(
        "messages.html",
        chat=chat_data,
        chat_id=chat_id,
        user=user,
        buyer_name=buyer_name,
        seller_name=seller_name,
        get_name=get_name  
    )


@app.route("/report/<chat_id>", methods=["POST"])
def report(chat_id):
    if "user" not in session:
        return redirect(url_for("login"))

    reason = request.form.get("reason")
    chats = load_chats()

    if chat_id in chats:
        chats[chat_id]["reported"] = True
        chats[chat_id].setdefault("messages", []).append({
            "sender": "SYSTEM",
            "text": f"Conversation reported: {reason}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M") 
        })
        chats[chat_id]["unread_for_admin"] = True  
        save_chats(chats)

    flash("Conversation reported to admin.", "warning")
    return redirect(url_for("chat", chat_id=chat_id))


@app.route("/admin_chat/<chat_id>", methods=["POST"])
def admin_chat(chat_id):
    if "user" not in session or not session.get("is_admin", False):
        return redirect(url_for("login"))

    chats = load_chats()
    if chat_id not in chats:
        return redirect(url_for("items"))

    msg = request.form["message"]
    if msg.strip():
        chats[chat_id]["messages"].append({
            "sender": "ADMIN",
            "text": msg,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")

        })
        save_chats(chats)
    return redirect(url_for("chat", chat_id=chat_id))


@app.route("/inbox")
def inbox():
    if "user" not in session:
        return redirect(url_for("login")) 

    email = session["user"]
    role = session.get("role")

    chats = load_chats()
    users = load_users()
    conversations = []

    for cid, chat in chats.items():
        if role == "admin":

            if chat.get("reported", False):
                conversations.append({
                    "chat_id": cid,
                    "other_user": get_name(chat["seller"]),
                    "last_message": chat["messages"][-1]["text"] if chat["messages"] else "",
                    "timestamp": chat["messages"][-1]["timestamp"] if chat["messages"] else "",
                    "unread": chat.get("unread_for_admin", False)
                })
        else:
            if email in [chat["buyer"], chat["seller"]]:
                other_email = chat["seller"] if email == chat["buyer"] else chat["buyer"]
                conversations.append({
                    "chat_id": cid,
                    "other_user": get_name(other_email),
                    "last_message": chat["messages"][-1]["text"] if chat["messages"] else "",
                    "timestamp": chat["messages"][-1]["timestamp"] if chat["messages"] else "",
                    "unread": chat.get("unread_for", {}).get(email, False)
                })

    return render_template("inbox.html", conversations=conversations)








