from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Config:
  SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost:5432/dytec"
