from flask import Blueprint, request, jsonify, g
from server.models.test import Test
from server.utils.database import db
from server.utils.login_required import login_required


tests_bp = Blueprint("tests", __name__)


@tests_bp.route("/", methods=["GET"])
@login_required
def get_all_tests():
  page = request.args.get("page", default=1, type=int)
  limit = request.args.get("limit", default=10, type=int)

  user = g.user

  pagination = (
    db.session.query(Test)
    .filter_by(user_id=user.id)
    .order_by(Test.created_at.desc())
    .paginate(page=page, per_page=limit, error_out=False)
  )
  tests = [test.to_simple_dict() for test in pagination.items]
  return jsonify(
    {
      "total": pagination.total,
      "pages": pagination.pages,
      "page": page,
      "limit": limit,
      "tests": tests,
    }
  )


@tests_bp.route("/<int:test_id>", methods=["GET"])
@login_required
def get_test_by_id(test_id):
  user = g.user

  test = (
    db.session.query(Test).filter(Test.user_id == user.id, Test.id == test_id).first()
  )

  if test is None:
    return jsonify({"pesan": "Tidak ada tes"}), 404

  return jsonify(test.to_dict())
