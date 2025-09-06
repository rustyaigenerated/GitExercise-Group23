import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 📸 Upload folder settings
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB

# Load listings from JSON
def load_listings():
    if not os.path.exists("listings.json"):
        return []
    with open("listings.json", "r") as f:
        return json.load(f)

# Save listings back to JSON
def save_listings(data):
    with open("listings.json", "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    return redirect("/listings")  # redirect homepage to listings

@app.route("/listings")
def listings():
    search = request.args.get("search", "").lower()
    category = request.args.get("category", "")

    data = load_listings()

    # Apply filters
    if search:
        data = [item for item in data if search in item["name"].lower() or search in item["description"].lower()]
    if category:
        data = [item for item in data if item["category"] == category]

    return render_template("listings.html", listings=data)

@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        data = load_listings()

        # Handle photo upload
        photo = request.files.get("photo")
        photo_filename = ""
        if photo and photo.filename != "":
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            photo_filename = photo.filename
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
            photo.save(file_path)

        # Create new item
        new_item = {
            "name": request.form["name"],
            "category": request.form["category"],
            "price": request.form["price"],
            "description": request.form["description"],
            "photo": photo_filename
        }

        data.append(new_item)
        save_listings(data)
        return redirect("/listings")

    return render_template("add item.html")


if __name__ == "__main__":
    app.run(debug=True)



