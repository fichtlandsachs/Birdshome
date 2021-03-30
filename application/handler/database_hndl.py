from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from application.models import birdsActivity, climate
from datetime import datetime as dt

import pandas as pd

class DBHandler():
    def __init__(self, engine=None):
        if engine is None:
            engine = create_engine('sqlite:////etc/birdshome/birdshome_base.db')

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
        birdsActivities = pd.read_sql_query('SELECT strftime("%d.%m.%Y", id) as Datum, strftime("%H:%M:%S", id) as Zeit from birds_activity;',self.conn)
        self.conn.close()
        return birdsActivities

    def create_climate_Record(self, db, temp, hum, pres):
        climateRecord = climate(id=dt.now().isoformat(), temperature=temp, humidity=hum, pressure=pres)
        self.session.add(climateRecord)
        self.session.commit()

    def getAllClimateRecords(self):
        clim_recs = pd.read_sql_query('select strftime("%d.%m.%Y", id) as Datum, strftime("%H:%M:%S", id) as Zeit, temperature as Temperatur, humidity as Luftfeuchtigkeit, pressure as Luftdruck, density as Helligkeit, temp_nest as TempNest from climate;', self.conn)
        return clim_recs
