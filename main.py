from flask import Flask, request, jsonify
from flask_talisman import Talisman
import pandas as pd
import xgboost as xgb
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

Talisman(app)

dysc_model = xgb.XGBClassifier()
dysc_model.load_model(os.path.join(BASE_DIR, "models", "dyscalculia.json"))

dot_stanine_model = xgb.XGBRegressor()
dot_stanine_model.load_model(os.path.join(BASE_DIR, "models", "dot_stanine.json"))

stroop_stanine_model = xgb.XGBRegressor()
stroop_stanine_model.load_model(os.path.join(BASE_DIR, "models", "stroop_stanine.json"))

add_stanine_model = xgb.XGBRegressor()
add_stanine_model.load_model(os.path.join(BASE_DIR, "models", "add_stanine.json"))

mult_stanine_model = xgb.XGBRegressor()
mult_stanine_model.load_model(os.path.join(BASE_DIR, "models", "mult_stanine.json"))

subs_stanine_model = xgb.XGBRegressor()
subs_stanine_model.load_model(os.path.join(BASE_DIR, "models", "subs_stanine.json"))


@app.route("/", methods=["POST"])
def predict():
  data = request.get_json()

  fields = [
    "age",
    "srt",
    "dot_rt",
    "dot_acc",
    "stroop_rt",
    "stroop_acc",
    "add_rt",
    "add_acc",
    "mult_rt",
    "mult_acc",
    "subs_rt",
    "subs_acc",
  ]

  missing = [field for field in fields if field not in data]
  if missing:
    return jsonify({"error": f"Missing fields: {missing}"}), 400

  fields.remove("subs_rt")
  fields.remove("subs_acc")

  input = pd.DataFrame([{field: data[field] for field in fields}])
  predictions = [
    dot_stanine_model.predict(input)[0],
    stroop_stanine_model.predict(input)[0],
    add_stanine_model.predict(input)[0],
    mult_stanine_model.predict(input)[0],
  ]

  input_stanine = pd.DataFrame(
    [
      {
        "age": data.get("age"),
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
        "age": data.get("age"),
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
  print(res)

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


if __name__ == "__main__":
  app.run()
