from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import ParticipantInformation


def get_information(db: Session):
    return db.execute(text('select * from participant_informations')).all()