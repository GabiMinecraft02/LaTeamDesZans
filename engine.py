import os
from flask import Flask, render_template, request, redirect, session, url_for
from dotenv import load_dotenv
from functools import wraps

# ---------- ENV ----------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
MEMBER_PASSWORD = os.getenv("MEMBER_PASSWORD")

# ---------- FAKE DB ----------
members = []
member_id = 1


# ---------- DECORATORS ----------
def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated
    return wrapper


# ---------- ROUTES ----------
@app.route("/")
def public():
    return render_template("public.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["user"] = "admin"
            session["role"] = "admin"
            return redirect("/admin")

        if password == MEMBER_PASSWORD:
            session["user"] = "member"
            session["role"] = "member"
            return redirect("/members")

    return render_template("login.html")


@app.route("/members")
@login_required(role="member")
def members_page():
    return render_template("members.html")


@app.route("/admin")
@login_required(role="admin")
def admin():
    return render_template("admin.html", members=members)


@app.route("/admin/add", methods=["POST"])
@login_required(role="admin")
def admin_add():
    global member_id

    members.append({
        "id": member_id,
        "pseudo": request.form["pseudo"],
        "jeux": request.form.get("jeux", ""),
        "fonction": request.form.get("fonction", ""),
        "role": request.form.get("role", "")
    })

    member_id += 1
    return redirect("/admin")


@app.route("/admin/delete/<int:id>")
@login_required(role="admin")
def admin_delete(id):
    global members
    members = [m for m in members if m["id"] != id]
    return redirect("/admin")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
