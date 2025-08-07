from flask import Blueprint, request, jsonify, g
import pandas as pd
import xgboost as xgb
import os
from server.utils.database import db
import statistics
from server.utils.login_required import login_required
from server.utils.verify_correct_answers import verify_correct_answers
from server.models.test import Test
from sqlalchemy.exc import IntegrityError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

predict_bp = Blueprint("predict", __name__)

dysc_model = xgb.XGBClassifier()
dysc_model.load_model(
  os.path.abspath(os.path.join(BASE_DIR, "..", "..", "models", "dyscalculia.json"))
)

dot_stanine_model = xgb.XGBRegressor()
dot_stanine_model.load_model(
  os.path.abspath(os.path.join(BASE_DIR, "..", "..", "models", "dot_stanine.json"))
)

stroop_stanine_model = xgb.XGBRegressor()
stroop_stanine_model.load_model(
  os.path.abspath(os.path.join(BASE_DIR, "..", "..", "models", "stroop_stanine.json"))
)

add_stanine_model = xgb.XGBRegressor()
add_stanine_model.load_model(
  os.path.abspath(os.path.join(BASE_DIR, "..", "..", "models", "add_stanine.json"))
)

mult_stanine_model = xgb.XGBRegressor()
mult_stanine_model.load_model(
  os.path.abspath(os.path.join(BASE_DIR, "..", "..", "models", "mult_stanine.json"))
)

subs_stanine_model = xgb.XGBRegressor()
subs_stanine_model.load_model(
  os.path.abspath(os.path.join(BASE_DIR, "..", "..", "models", "subs_stanine.json"))
)


@predict_bp.route("", methods=["POST"])
@login_required
def predict():
  user = g.user
  data = request.get_json()
  fields = [
    "srt",
    "dot_user_answer",
    "dot_rt",
    "stroop_user_answer",
    "stroop_rt",
    "add_user_answer",
    "add_rt",
    "subs_user_answer",
    "subs_rt",
    "mult_user_answer",
    "mult_rt",
    "correct_answers",
  ]

  missing = [field for field in fields if field not in data]
  if missing:
    return jsonify({"pesan": f"Tidak ada {missing}"}), 400

  if user.age is None:
    return jsonify({"pesan": "Tidak dapat menyelesaikan permintaan"}), 400

  # Kurang verify id_test sg ws digwe pas ngepost ng x

  valid, correct_answers = verify_correct_answers(data, user.key)
  if not valid:
    return jsonify({"pesan": "Tidak dapat menyelesaikan permintaan"}), 400

  subtests = ["dot", "stroop", "add", "subs", "mult"]

  accuracy_results = {}

  for subtest in subtests:
    user_key = f"{subtest}_user_answer"
    correct_key = f"{subtest}_correct_answer"

    user_answers = data.get(user_key, [])
    correct = correct_answers.get(correct_key, [])

    if len(user_answers) != len(correct):
      return jsonify({"error": f"Answer length mismatch for {subtest}"}), 400

    correct_count = sum(1 for u, c in zip(user_answers, correct) if u == c)
    accuracy = correct_count / len(correct)
    accuracy_results[f"{subtest}_acc"] = round(accuracy, 2)

  required = [
    "age",
    "srt",
    "dot_rt",
    "dot_acc",
    "stroop_rt",
    "stroop_acc",
    "add_rt",
    "add_acc",
    "subs_rt",
    "subs_acc",
    "mult_rt",
    "mult_acc",
  ]

  calculated = {}

  calculated["age"] = int(user.age)

  for field in required:
    if field.endswith("_rt") or field == "srt":
      calculated[f"{field}"] = statistics.median(data[field])
    elif field.endswith("_acc"):
      calculated[field] = accuracy_results[field]

  excluded_keys = {"subs_acc", "subs_rt"}

  input = pd.DataFrame(
    [{k: v for k, v in calculated.items() if k not in excluded_keys}]
  )
  predictions = [
    dot_stanine_model.predict(input)[0],
    stroop_stanine_model.predict(input)[0],
    add_stanine_model.predict(input)[0],
    mult_stanine_model.predict(input)[0],
  ]

  input_stanine = pd.DataFrame(
    [
      {
        "age": user.age,
        "dot_stanine": predictions[0],
        "stroop_stanine": predictions[1],
        "add_stanine": predictions[2],
        "mult_stanine": predictions[3],
      }
    ]
  )
  subs_stanine = subs_stanine_model.predict(input_stanine)[0]

  stanines = pd.DataFrame(
    [
      {
        "age": user.age,
        "dot_stanine": predictions[0],
        "stroop_stanine": predictions[1],
        "add_stanine": predictions[2],
        "mult_stanine": predictions[3],
        "subs_stanine": subs_stanine,
      }
    ]
  )
  label = dysc_model.predict(stanines)[0]
  probs = dysc_model.predict_proba(stanines)[0]
  clean_probs = [float(x) for x in probs]

  res = [float(x) for x in predictions] + [float(subs_stanine)]

  test = Test(
    user_id=user.id,
    srt=calculated["srt"],
    dot_rt=calculated["dot_rt"],
    dot_acc=calculated["dot_acc"],
    dot_stanine=res[0],
    stroop_rt=calculated["stroop_rt"],
    stroop_acc=calculated["stroop_acc"],
    stroop_stanine=res[1],
    add_rt=calculated["add_rt"],
    add_acc=calculated["add_acc"],
    add_stanine=res[2],
    subs_rt=calculated["subs_rt"],
    subs_acc=calculated["subs_acc"],
    subs_stanine=res[4],
    mult_rt=calculated["mult_rt"],
    mult_acc=calculated["mult_acc"],
    mult_stanine=res[3],
    label=int(label),
    dysc_prob=clean_probs[1],
  )
  db.session.add(test)

  try:
    db.session.commit()
  except IntegrityError:
    db.session.rollback()
    return jsonify({"pesan": "Masalah internal server"}), 500

  return jsonify(
    {
      "diagnosis": int(label),
      "probabilitas": {"0": clean_probs[0], "1": clean_probs[1], "2": clean_probs[2]},
      "skor": res,
      "label": {
        "diagnosis": {
          "0": "Normal",
          "1": "Diskalkulia",
          "2": "Keterampilan Aritmatika yang Buruk",
        },
        "skor": [
          "Menghitung Titik",
          "Perbandingan Angka",
          "Pertambahan",
          "Perkalian",
          "Pengurangan",
        ],
      },
    }
  )
