from sqlalchemy import String, Column, Integer, func
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.ext.declarative import declarative_base

from application import db

Base = declarative_base()


class birdsActivity(db.Model):
    __tablename__ = 'birds_activity'
    id = Column(DATETIME,
                primary_key=True,
                index=False,
                unique=True,
                nullable=False,
                default=func.to_char())
    sensor = Column(String(64),
                    index=False,
                    unique=False,
                    nullable=False)


class climate(db.Model):
    __tablename__ = 'climate'
    id = Column(DATETIME, primary_key=True, index=True, unique=True, nullable=False)
    temperature = Column(Integer, primary_key=False, index=False, unique=False)
    humidity = Column(Integer, primary_key=False, index=False, unique=False)
    pressure = Column(Integer, primary_key=False, index=False)
    density = Column(Integer, primary_key=False, index=False)
    temp_nest = Column(Integer, primary_key=False, index=False, unique=False)
