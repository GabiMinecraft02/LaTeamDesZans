from flask import Flask, render_template, redirect, session, request
import os
from supabase import create_client

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "FLASK")

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Passwords
MEMBER_PASSWORD = os.getenv("PASSWORD")
ADMIN_PASSWORD = os.getenv("AD_PASSWORD")

@app.route("/")
def home():
    return redirect("/public")

@app.route("/public")
def public():
    return render_template("public.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pw = request.form.get("password")
        if pw == ADMIN_PASSWORD:
            session["role"] = "admin"
            return redirect("/admin")
        elif pw == MEMBER_PASSWORD:
            session["role"] = "member"
            return redirect("/members")
        else:
            return render_template("login.html", error="Mot de passe incorrect")
    return render_template("login.html")

@app.route("/members")
def members():
    if "role" not in session:
        return redirect("/login")
    if session["role"] != "member":
        return "Accès interdit", 403

    data = supabase.table("members").select("*").order("id").execute()
    return render_template("members.html", members=data.data)

@app.route("/admin")
def admin():
    if "role" not in session or session["role"] != "admin":
        return redirect("/login")

    data = supabase.table("members").select("*").order("id").execute()
    return render_template("admin.html", members=data.data)


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
