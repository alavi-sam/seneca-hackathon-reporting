from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from db import get_db



auth_router = APIRouter(prefix='/report')



@auth_router.get('/download-csv')
def get_first_participant(db: Session = Depends(get_db)):
    data = get_information(db)

    file_path = 'participants_information.csv'
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        header = [
            'MemberNumber',
            'FirstName',
            'LastName',
            'Email',
            'TeamName',
            'IsLeader',
            'ShirtSize',
            'FromSeneca',
            'IsAlumni',
            'SchoolName',
            'GraduationYear',
            'SemesterNumber',
            'StudyFieldName',
            'ProgramName',
            'DegreeType',
            'IsSolo',
            'HavingTeam',
            'RegisterTime(UTC0)'
        ]

        participants = [
        (participant_data.member_number,
        participant_data.firstname.strip() if participant_data.firstname else '',
        participant_data.lastname.strip() if participant_data.lastname else '',
        participant_data.email,
        participant_data.team_name,
        participant_data.is_leader,
        participant_data.shirt_size.strip() if participant_data.shirt_size else '',
        participant_data.from_seneca,
        participant_data.is_alumni,
        participant_data.school_name or '',
        participant_data.graduation_year.strip() if participant_data.graduation_year else '',
        participant_data.semester_number,
        participant_data.study_field_name or '',
        participant_data.program_name,
        participant_data.degree_type or '',
        participant_data.is_solo,
        participant_data.having_team,
        participant_data.registered_at.strftime("%Y-%m-%d %H:%M:%S") if participant_data.registered_at else '')
        for participant_data in data
    ]
        # print(participants)
        print('HELLO WORLD')
        writer.writerow(header)

        writer.writerows(participants)
    print('hello')
    return FileResponse(file_path, media_type='text/csv', filename='participants_information.csv')