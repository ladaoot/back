from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList

from database import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    experience = Column(String)
    employer = Column(String)
    salary_from = Column(Integer, nullable=True)
    salary_to = Column(Integer, nullable=True)
    salary_currency = Column(String)
    is_archived = Column(Boolean)
