from flask import Flask
from flask_talisman import Talisman
from server.utils.database import db, Config
from sqlalchemy import inspect
from server.utils.generate_random_questions import generate_questions

from server.routes.predict import predict_bp
from server.routes.login import login_bp
from server.routes.tests import tests_bp

import server.models.user
import server.models.test
import server.models.question

app = Flask(__name__)

Talisman(app, force_https=False)

app.config.from_object(Config)
db.init_app(app)

with app.app_context():
  db.create_all()

  print("Registered tables:", db.metadata.tables.keys())

  inspector = inspect(db.engine)
  print("Actual DB tables:", inspector.get_table_names())


# ---------------------------------------------

app.register_blueprint(predict_bp, url_prefix="/predict")
app.register_blueprint(login_bp, url_prefix="/login")
app.register_blueprint(tests_bp, url_prefix="/tests")


if __name__ == "__main__":
  app.run(debug=True)

# if __name__ == "__main__":
#   app.run(host="0.0.0.0", port=80, debug=True)
