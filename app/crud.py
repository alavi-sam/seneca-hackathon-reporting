from sqlalchemy.orm import Session
from app.models import ParticipantInformation


def get_information(db: Session):
    return db.query(ParticipantInformation).all()