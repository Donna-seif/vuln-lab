from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, UserMixin, login_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-only-not-a-real-secret"   # local lab only
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vulnapp.db"

db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {"id": self.id, "owner_id": self.owner_id,
                "amount": self.amount, "description": self.description}


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.post("/login")
def login():
    data = request.get_json() or {}
    user = db.session.query(User).filter_by(username=data.get("username")).first()
    if user is None or not check_password_hash(user.password_hash, data.get("password", "")):
        abort(401)
    login_user(user)
    return jsonify({"logged_in_as": user.username, "user_id": user.id})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/invoices/")
@login_required
def list_invoices():
    invoices = (
        db.session.query(Invoice)
        .filter(Invoice.owner_id == current_user.id)
        .all()
    )
    return jsonify([inv.to_dict() for inv in invoices])


@app.get("/api/invoices/<int:invoice_id>")
@login_required
def get_invoice(invoice_id):
    invoice = db.session.get( Invoice, invoice_id)
    if invoice is None:
        abort(404)
    return jsonify(invoice.to_dict())

def seed():
    db.drop_all()
    db.create_all()
    alice = User(username="alice", password_hash=generate_password_hash("alice123"))
    bob = User(username="bob", password_hash=generate_password_hash("bob123"))
    db.session.add_all([alice, bob])
    db.session.commit()
    # Interleaved on purpose, so the IDs alternate between users
    db.session.add_all([
        Invoice(owner_id=alice.id, amount=120, description="Alice - web hosting"),
        Invoice(owner_id=bob.id,   amount=980, description="Bob - legal retainer"),
        Invoice(owner_id=alice.id, amount=45,  description="Alice - domain renewal"),
        Invoice(owner_id=bob.id,   amount=3000, description="Bob - payroll Q4"),
    ])
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        seed()
    app.run(host="127.0.0.1", port=5000, debug=True)
