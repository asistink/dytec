from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Config:
  SQLALCHEMY_DATABASE_URI = "postgresql://postgres:dysec123@localhost:5432/dytec"
