from flask import Blueprint, jsonify, request, g
from server.utils.database import db
from server.utils.login_required import login_required

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/", methods=["PUT"])
@login_required

def update_age():
  user = g.user
  data = request.get_json()
  if not data:
      return jsonify({"error": "Data tidak ditemukan"}), 400

  age = data.get("age")
  if not data.get("age"):
      return jsonify({"error": "Age tidak ditemukan"}), 400
  try:
        age = int(age)
  except ValueError:
        return jsonify({"error": "Age harus berupa angka"}), 400

  user.age = age
  db.session.commit()
  return jsonify({"success": "Age berhasil diubah"}), 200
