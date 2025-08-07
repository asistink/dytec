from flask import Blueprint, request, jsonify, g
from server.utils.database import db
from server.models.user import User
from sqlalchemy.exc import IntegrityError
from cryptography.fernet import Fernet
from google.auth.transport import requests as grequests
from google.oauth2 import id_token

login_bp = Blueprint("login", __name__)

CLIENT_ID = "187016501799-dsmoe3s5bkh6gsq1g0v1dc43vq4qsjj0.apps.googleusercontent.com"


@login_bp.route("", methods=["POST"])
def login():
  auth_header = request.headers.get("Authorization")
  token = auth_header.split(" ")[1]
  try:
    id_info = id_token.verify_oauth2_token(token, grequests.Request(), CLIENT_ID)
    g.user = id_info
  except Exception as _:
    return jsonify({"error": "Token tidak valid"}), 403

  email = id_info.get("email")
  name = id_info.get("name")
  picture = id_info.get("picture")

  user = db.session.query(User).filter_by(email=email).first()

  if not user:
    key = Fernet.generate_key()
    user = User(email=email, name=name, picture=picture, key=key.decode())
    db.session.add(user)
    try:
      db.session.commit()
    except IntegrityError:
      db.session.rollback()
      return jsonify({"pesan": "Masalah internal server"}), 500

  return jsonify({"pesan": "Login berhasil"})
