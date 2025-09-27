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






