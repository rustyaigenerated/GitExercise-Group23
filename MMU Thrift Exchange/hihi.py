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






