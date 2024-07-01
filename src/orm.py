from sqlalchemy.orm import Session

import models
import schemas


def mapping_from_schemas_to_models(schemas_model: schemas.VacancyModel, db: Session):
    model = get_vacancy_by_id(db, schemas_model.id)

    if model is None:
        model = models.Vacancy(id=schemas_model.id)

    model.experience = schemas_model.experience
    model.salary_currency = schemas_model.salary_currency
    model.salary_to = schemas_model.salary_to
    model.salary_from = schemas_model.salary_from
    model.employer = schemas_model.employer
    model.name = schemas_model.name
    model.is_archived = schemas_model.is_archived

    return model


def create_vacancy(db: Session, vacancy: schemas.VacancyModel):
    db_vacancy = mapping_from_schemas_to_models(vacancy, db)

    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy


def get_all_vacancies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vacancy).offset(skip).limit(limit).all()


def get_vacancy_by_id(db: Session, vacancy_id: int):
    return db.get(models.Vacancy, vacancy_id)


def update_vacancies(db: Session, vacancy: schemas.VacancyModel):
    mapping_from_schemas_to_models(vacancy, db)
    db.commit()
