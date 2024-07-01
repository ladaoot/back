from typing import Union

import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

import constants
import models
import orm
import schemas
from database import SessionLocal, engine

app = FastAPI()

roles = []
categories = []


@app.on_event("startup")
async def startup_event():
    models.Base.metadata.create_all(bind=engine)

    if constants.OAUTH_TOKEN == '':
        response = requests.post(
            url=f'https://hh.ru/oauth/token?grant_type=client_credentials&client_id={constants.CLIENT_ID}'
                f'&client_secret={constants.CLIENT_SECRET}')
        r = response.json()
        constants.OAUTH_TOKEN = r['access_token']

    url = 'https://api.hh.ru/professional_roles'

    headers = {'OauthToken': constants.OAUTH_TOKEN}

    response = requests.get(url, headers=headers)
    cat = response.json()["categories"]

    for c in cat:
        item = {"name": c["name"], "id": c["id"]}

        for r in c["roles"]:
            roles.append({"name": r["name"], "id": r["id"], "category": c["id"]})

        categories.append(item)


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
        raise HTTPException(status_code=response.status_code, detail="Unable to fetch vacancies")


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
        vacancy.is_archived = item["archived"]
        vacancies_data.append(vacancy)
    return vacancies_data


@app.get("/vacancies")
async def vacancies(filters: Union[schemas.Filter, None] = None, db: Session = Depends(get_db)):
    items = get_vacancies(filters)

    vacancies_data = map_from_hh_object_to_vacancies(items)

    for vacancy in vacancies_data:
        if orm.get_vacancy_by_id(db, vacancy.id):
            orm.update_vacancies(db, vacancy=vacancy)
        else:
            orm.create_vacancy(db=db, vacancy=vacancy)

    res = {"found": items["found"], "vacancies": jsonable_encoder(vacancies_data)}

    return JSONResponse(content=res)


@app.get("/filters/categories")
async def filters_categories():
    return categories


@app.get("/filters/categories/{cat_id}")
async def get_roles_by_category(cat_id: str):
    res = []
    for role in roles:
        if role["category"] == cat_id:
            res.append(role)

    return res
