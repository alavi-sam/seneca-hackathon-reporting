from sqlalchemy import BigInteger, Boolean, CHAR, CheckConstraint, Column, DateTime, Enum, ForeignKey, Integer, SmallInteger, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class ParticipantInformation(Base):
    __tablename__ = 'participant_informations'

    member_number = Column(BigInteger, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    email = Column(String(80))
    team_name = Column(String(50))
    is_leader = Column(Boolean)
    shirt_size = Column(CHAR(3))
    from_seneca = Column(Boolean)
    is_alumni = Column(Boolean)
    school_name = Column(String(200))
    graduation_year = Column(CHAR(4))
    semester_number = Column(SmallInteger)
    degree_type = Column(Enum('Certificate', 'Diploma', 'Advanced Diploma', 'Bachelors', 'Postgraduate Certificate', 'Postgraduate Diploma', 'Masters', 'Phd', name='fixed_degree_types'))
    study_field_name = Column(Enum('Computer Science', 'Business Administration', 'Psychology', 'Biology', 'Electrical Engineering', 'Nursing', 'English Literature', 'History', 'Mathematics', 'Chemistry', 'Economics', 'Political Science', 'Environmental Science', 'Mechanical Engineering', 'Graphic Design', 'Communications', 'Sociology', 'Education (Elementary)', 'Accounting', 'Marketing', 'Physics', 'Philosophy', 'Civil Engineering', 'Data Science', 'Hospitality Management', 'Information Technology', name='fixed_area_studies'))
    program_name = Column(String(80))
    is_solo = Column(Boolean)
    having_team = Column(Boolean)
    registered_at = Column(DateTime(True))


class School(Base):
    __tablename__ = 'school'

    school_id = Column(Integer, primary_key=True, server_default=text("nextval('school_school_id_seq'::regclass)"))
    school_name = Column(String(200), nullable=False)
    province = Column(String(30))
    city = Column(String(50))


class SenecaProgram(Base):
    __tablename__ = 'seneca_programs'

    program_id = Column(Integer, primary_key=True, server_default=text("nextval('seneca_programs_program_id_seq'::regclass)"))
    program_name = Column(String(80))


class Sponsor(Base):
    __tablename__ = 'sponsors'
    __table_args__ = (
        CheckConstraint("(contact_email)::text ~ '^[a-zA-Z0-9._%%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'::text"),
        CheckConstraint("contact_phonenumber ~ '^[0-9]{10}$'::text")
    )

    sponsor_id = Column(Integer, primary_key=True, server_default=text("nextval('sponsors_sponsor_id_seq'::regclass)"))
    contact_firstname = Column(String(50), nullable=False)
    contact_lastname = Column(String(50), nullable=False)
    contact_email = Column(String(60), nullable=False, unique=True)
    company_name = Column(String(50), nullable=False)
    contact_phonenumber = Column(CHAR(10), unique=True)
    contact_position = Column(String(30))
    description = Column(Text)


class Team(Base):
    __tablename__ = 'teams'
    __table_args__ = (
        CheckConstraint('((is_private = true) AND (team_passcode IS NOT NULL)) OR ((is_private = false) AND (team_passcode IS NULL))'),
    )

    team_id = Column(Integer, primary_key=True, server_default=text("nextval('teams_team_id_seq'::regclass)"))
    team_name = Column(String(50), nullable=False, unique=True)
    team_passcode = Column(String(20))
    is_private = Column(Boolean, nullable=False)
    created_at = Column(DateTime(True), server_default=text("now()"))


class Participant(Base):
    __tablename__ = 'participants'
    __table_args__ = (
        CheckConstraint("(email)::text ~ '^[a-zA-Z0-9._%%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'::text"),
        CheckConstraint("phone_number ~ '^[0-9]{10}$'::text")
    )

    participant_id = Column(Integer, primary_key=True, server_default=text("nextval('participants_participant_id_seq'::regclass)"))
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    email = Column(String(80), nullable=False, unique=True)
    phone_number = Column(CHAR(10), nullable=False, unique=True)
    is_alumni = Column(Boolean, nullable=False)
    graduation_year = Column(CHAR(4))
    graduation_month = Column(String(2))
    from_seneca = Column(Boolean, nullable=False)
    school_id = Column(ForeignKey('school.school_id'))
    semester_number = Column(SmallInteger, nullable=False)
    shirt_size = Column(CHAR(3), nullable=False)
    seneca_program_id = Column(ForeignKey('seneca_programs.program_id'))
    is_solo = Column(Boolean, nullable=False)
    having_team = Column(Boolean, nullable=False)
    degree_type = Column(Enum('Certificate', 'Diploma', 'Advanced Diploma', 'Bachelors', 'Postgraduate Certificate', 'Postgraduate Diploma', 'Masters', 'Phd', name='fixed_degree_types'))
    study_field_name = Column(Enum('Computer Science', 'Business Administration', 'Psychology', 'Biology', 'Electrical Engineering', 'Nursing', 'English Literature', 'History', 'Mathematics', 'Chemistry', 'Economics', 'Political Science', 'Environmental Science', 'Mechanical Engineering', 'Graphic Design', 'Communications', 'Sociology', 'Education (Elementary)', 'Accounting', 'Marketing', 'Physics', 'Philosophy', 'Civil Engineering', 'Data Science', 'Hospitality Management', 'Information Technology', name='fixed_area_studies'))
    registered_at = Column(DateTime(True), server_default=text("now()"))

    school = relationship('School')
    seneca_program = relationship('SenecaProgram')


class TeamMember(Base):
    __tablename__ = 'team_members'

    team_id = Column(ForeignKey('teams.team_id'), primary_key=True, nullable=False)
    participant_id = Column(ForeignKey('participants.participant_id'), primary_key=True, nullable=False)
    is_leader = Column(Boolean, nullable=False, server_default=text("false"))
    joined_at = Column(DateTime(True), server_default=text("now()"))

    participant = relationship('Participant')
    team = relationship('Team')
