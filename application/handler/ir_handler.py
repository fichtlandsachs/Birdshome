#!/usr/bin/python

import RPi.GPIO as GPIO
import time, requests, responses
import datetime as dt
import sqlite3 as db

# BCM GPIO-Referenen verwenden (anstelle der Pin-Nummern)
# und GPIO-Eingang definieren
GPIO.setmode(GPIO.BCM)
GPIO_PIR = 16

# Set pin as input
GPIO.setup(GPIO_PIR, GPIO.IN)

# Initialisierung
Read = 0
State = 0

# Schleife, bis PIR == 0 ist
while GPIO.input(GPIO_PIR) != 0:
    time.sleep(0.1)
print('Bereit...')


# Callback-Funktion
def MOTION(PIR_GPIO):
    print('Motion detected...')
    connection = db.connect('/home/pi/birdshome/birdshome_base.db')
    cursor = connection.cursor()
    vals = (dt.datetime.now().isoformat(), 'IR_1')
    sql = 'INSERT INTO birds_activity (id, sensor) values' + str(vals) + ";"
    values = []
    cursor.execute(sql, values)
    connection.commit()
    connection.close()
    resp = requests.get('http://localhost:5000/capture')
    print(resp.status_code)


try:
    # Ereignis definieren: steigende Flanke
    GPIO.add_event_detect(GPIO_PIR, GPIO.RISING, callback=MOTION)
    while True:
        time.sleep(2)

finally:
    GPIO.cleanup()
