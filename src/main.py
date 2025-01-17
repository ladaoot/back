from typing import Union

import requests

from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import orm, schemas, models, constants
from database import SessionLocal, engine

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    models.Base.metadata.create_all(bind=engine)

    if constants.OAUTH_TOKEN == '':
        response = requests.post(
            url=f'https://hh.ru/oauth/token?grant_type=client_credentials&client_id={constants.CLIENT_ID}'
                f'&client_secret={constants.CLIENT_SECRET}')
        r = response.json()
        constants.OAUTH_TOKEN = r['access_token']


@app.on_event("shutdown")
def shutdown_event():
    models.Base.metadata.drop_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_vacancies(params=None):
    url = 'https://api.hh.ru/vacancies'

    headers = {'OauthToken': constants.OAUTH_TOKEN}

    response = requests.get(url, params=params, headers=headers)
    print(response.url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Unable to fetch vacancies"}


def map_from_hh_object_to_vacancies(items):
    vacancies_data = []
    for item in items["items"]:
        vacancy = schemas.VacancyModel()
        experience = item["experience"]
        employer = item["employer"]
        salary = item["salary"]
        vacancy.experience = experience["name"]
        vacancy.employer = employer["name"]
        if salary is not None:
            vacancy.salary_from = salary["from"]
            vacancy.salary_to = salary["to"]
            vacancy.salary_currency = salary["currency"]
        vacancy.name = item["name"]
        vacancy.id = int(item["id"])
        vacancies_data.append(vacancy)
    return vacancies_data


@app.get("/vacancies")
async def vacancies(filters: Union[schemas.Filter, None] = None, db: Session = Depends(get_db)):
    v = orm.get_vacancies(db)
    v_id = []
    for vv in v:
        v_id.append(vv.id)

    if filters is not None:
        items = get_vacancies(filters)
    else:
        items = get_vacancies()

    vacancies_data = map_from_hh_object_to_vacancies(items)

    for vacancy in vacancies_data:
        if vacancy.id not in v_id:
            orm.create_vacancy(db=db, vacancy=vacancy)
        else:
            orm.update_vacancies(db, vacancy=vacancy)
    return vacancies_data
