from datetime import datetime as dt

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.models import birdsActivity, climate, appConfig


class DBHandler:
    def __init__(self, dbUrl):

        engine = create_engine(url=dbUrl)
        self.conn = engine.connect()
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def create_birdMove(self, sensor):
        act = birdsActivity(id=dt.now(), sensor=sensor)
        self.session.add(act)
        self.session.commit()
        self.close()

    def close(self):
        self.session.close()
        self.conn.close()

    def getAllActivity(self):
        birdsActivities = pd.read_sql_query(
            'SELECT strftime("%d.%m.%Y", id) as Datum, strftime("%H:%M:%S", id) as Zeit from birds_activity;',
            self.conn)
        self.conn.close()
        return birdsActivities

    def create_climate_Record(self, db, temp, hum, pres):
        climateRecord = climate(id=dt.now().isoformat(), temperature=temp, humidity=hum, pressure=pres)
        self.session.add(climateRecord)
        self.session.commit()
        self.close()

    def getAllClimateRecords(self):
        clim_recs = pd.read_sql_query(
            'select strftime("%d.%m.%Y", id) as Datum, strftime("%H:%M:%S", id) as Zeit, temperature as Temperatur, '
            'humidity as Luftfeuchtigkeit, pressure as Luftdruck, density as Helligkeit, temp_nest as TempNest from '
            'climate;',
            self.conn)
        self.close()
        return clim_recs

    def getConfigEntry(self, app_area, config_key):
        if self.checkConfigEntryExists(app_area, config_key):
            entry = self.session.query(appConfig).filter_by(config_area=app_area, config_key=config_key).first()
            self.close()
            if entry is not None:
                return entry.config_value
            else:
                return None
        else:
            return None

    def checkConfigEntryExists(self, app_area, config_key):
        entry = self.session.query(appConfig).filter_by(config_area=app_area, config_key=config_key).first()
        self.close()
        if entry is None:
            return False
        else:
            return True

    def getAllConfigEntriesForArea(self, app_area):
        entries = self.session.query(appConfig).filter_by(config_area=app_area).all()
        self.close()
        return entries

    def createUpdateConfigEntry(self, app_area, config_key, config_value):
        if self.checkConfigEntryExists(app_area, config_key):
            entry = self.session.query(appConfig).filter_by(config_area=app_area, config_key=config_key).first()
            entry.config_value = config_value
        else:
            configRecord = appConfig()
            configRecord.config_area = app_area
            configRecord.config_key = config_key
            configRecord.config_value = config_value
            self.session.add(configRecord)
        self.session.commit()
        self.close()
