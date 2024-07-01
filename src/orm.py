from sqlalchemy.orm import Session

from database import engine, Base
import schemas, models


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


def create_vacancy(db: Session, vacancy: schemas.VacancyModel):
    db_vacancy = models.Vacancy(id=vacancy.id)
    db_vacancy.experience = vacancy.experience
    db_vacancy.salary_currency = vacancy.salary_currency
    db_vacancy.salary_to = vacancy.salary_to
    db_vacancy.salary_from = vacancy.salary_from
    db_vacancy.employer = vacancy.employer
    db_vacancy.name = vacancy.name

    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy


def get_vacancies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vacancy).offset(skip).limit(limit).all()


def get_vacancy_by_id(db: Session, vacancy_id: int):
    return db.get(models.Vacancy, vacancy_id)


def update_vacancies(db: Session, vacancy: schemas.VacancyModel):
    v = get_vacancy_by_id(db, vacancy.id)
    v.experience = vacancy.experience
    v.salary_currency = vacancy.salary_currency
    v.salary_to = vacancy.salary_to
    v.salary_from = vacancy.salary_from
    v.employer = vacancy.employer
    v.name = vacancy.name
    db.commit()
