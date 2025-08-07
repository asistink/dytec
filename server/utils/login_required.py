from flask import request, jsonify, g
from functools import wraps
from server.utils.database import db
from server.models.user import User
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

CLIENT_ID = "187016501799-dsmoe3s5bkh6gsq1g0v1dc43vq4qsjj0.apps.googleusercontent.com"


def login_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
      return jsonify({"error": "Tidak terauthorisasi"}), 401

    token = auth_header.split(" ")[1]
    try:
      id_info = id_token.verify_oauth2_token(token, grequests.Request(), CLIENT_ID)

      user = db.session.query(User).filter_by(email=id_info["email"]).first()

      if not user:
        return jsonify({"pesan": "Tidak dapat menyelesaikan permintaan"}), 400

      g.user = user
    except Exception as _:
      return jsonify({"error": "Token tidak valid"}), 403

    return f(*args, **kwargs)

  return decorated
