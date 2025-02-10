from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import ReportUser


def get_information(db: Session):
    return db.query(ReportUser)