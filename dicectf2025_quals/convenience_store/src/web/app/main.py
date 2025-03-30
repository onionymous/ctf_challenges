import base64
from flask import Flask, render_template, request, redirect
import hashlib
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
import hashlib
import os
from pathlib import Path

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
SESSION_TYPE = "sqlalchemy"
app.secret_key = os.getenv("APP_SECRET_KEY")
if app.secret_key is None or app.secret_key == "":
    raise Exception("APP_SECRET_KEY is not set")
db = SQLAlchemy(app)
login = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    notes = db.relationship("Note", backref="owner", lazy=True)

    def __repr__(self):
        return "%s" % self.username


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return "<Post %r>" % self.title


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/")
def home():
    return render_template("index.html", current_user=current_user)


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        if username and password:
            if User.query.filter_by(username=username).first() is None:
                user = User(
                    username=username,
                    password=hashlib.sha256(str(password).encode("utf-8")).hexdigest(),
                )
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect("/notes")
            else:
                user = User.query.filter_by(
                    username=username,
                    password=hashlib.sha256(str(password).encode("utf-8")).hexdigest(),
                ).first()
                if user is not None:
                    login_user(user)
                    return redirect("/notes")
                else:
                    return "Failed", 500


@app.route("/notes", methods=["GET", "POST"])
def get_notes():
    if current_user.is_authenticated:
        if request.method == "GET":
            notes = current_user.notes
            return render_template("notes.html", notes=notes)
        elif request.method == "POST":
            title = request.form.get("title", None)
            body = request.form.get("body", None)
            if "dice{" in body:
                return redirect("/notes")
            user_note = Note(title=title, body=body, owner_id=current_user.id)
            db.session.add(user_note)
            db.session.commit()
            return redirect("/notes")

    return render_template("notes.html", current_user=current_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/search")
def search_notes():
    notes = []
    if current_user.is_authenticated:
        query = request.args.get("query", None)
        if query is not None:
            query = f"%{str(query)}%"
            notes = (
                Note.query.filter(
                    Note.body.like(query), Note.owner_id == current_user.id
                )
                .limit(100)
                .all()
            )
    return render_template(
        "search.html",
        notes=notes,
        current_user=current_user,
        inlined_note_b64="data:image/png;base64,"
        + base64.b64encode(Path("static/note.png").read_bytes()).decode("utf-8"),
    )


@app.route("/note/<int:note_id>")
def get_note(note_id):
    if current_user.is_authenticated:
        n = Note.query.filter(
            Note.id == note_id, Note.owner_id == current_user.id
        ).first()
        return render_template("note.html", note=n)
    return "Not logged in!"


@app.after_request
def add_headers(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["X-Frame-Options"] = "DENY"
    r.headers["Content-Security-Policy"] = (
        "script-src 'sha256-kmHvs0B+OpCW5GVHUNjv9rOmY0IvSIRcf7zGUDTDQM8=' 'sha384-7+zCNj/IqJ95wo16oMtfsKbZ9ccEh31eOz1HGyDuCQ6wgnyJNSYdrPa03rtR1zdB' 'sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p'; object-src 'none'; base-uri 'none'; frame-ancestors 'none';"
    )
    return r


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(host="0.0.0.0", port=8080, debug=False)
