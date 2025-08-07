from server.utils.database import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, JSON

class Consultation(db.Model):
  __tablename__ = "consultations"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str]
  whatsapp_number: Mapped[str]
  pricelist: Mapped[dict] = mapped_column(JSON)
  location: Mapped[str] = mapped_column(Text)
  photo: Mapped[str] = mapped_column(Text)

def to_dict(consultation: Consultation):
    return {
        "id": consultation.id,
        "name": consultation.name,
        "whatsapp_number": consultation.whatsapp_number,
        "pricelist": consultation.pricelist,
        "location": consultation.location,
        "photo": consultation.photo
    }