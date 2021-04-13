import datetime
import glob
import io
import os
import pathlib
import sqlite3
import threading
import time

from application.handler.database_hndl import DBHandler

try:
    from uwsgidecorators import *
    import uwsgi
except:
    pass
import cv2
import matplotlib.pyplot as plt
from flask import render_template, Response, send_file, g, request

from application import create_app

from application.handler.motion_handler import Motion_Handler

app = create_app()

# Erzeugen der Instanz für die Aufnahme
#
# da die Kamera für die Aufnahe für andere Programme dann gesperrt ist
# ist es erforderlich die Instanz an die weiteren Funktionen weiterzugeben
vc = cv2.VideoCapture(0)
vc.set(cv2.CAP_PROP_FPS, app.config['VID_FRAMES'])
vc.set(cv2.CAP_PROP_FRAME_WIDTH, app.config['VID_RES_X'])
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, app.config['VID_RES_Y'])

videoFolder = os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER_VID'])
pictureFolder = os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER_PIC'])
DATABASE = app.config['SQLALCHEMY_DATABASE_URI']


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def creat_BG_task():
    thread = threading.Thread(target=uwsgi_task)
    thread.start()


def uwsgi_task():
    mHandler = Motion_Handler(vc=vc, vidHeigth=app.config['VID_RES_X'], vidWidth=app.config['VID_RES_Y'],
                              fileNamePrefix=app.config['LATEST_VID'], folder=videoFolder)
    mHandler.detect()


# Erzeugen eines Hintergrundtask, welcher die Kamera permanent überwacht und be Bewegungen eine Aufzeichnung startet
creat_BG_task()


@app.route('/')
def start():
    videoFolder = os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER_VID'])
    list_of_files = glob.glob(videoFolder + '/*.avi')
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_file_time = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(os.stat(latest_file).st_ctime))
    num_filesToday = len(glob.glob(videoFolder + '/*' + str(datetime.datetime.today().day) + str(
        format(datetime.datetime.today().month, '02')) + str(datetime.datetime.today().year) + '*.avi'))
    num_files = len(glob.glob(videoFolder + '/*.avi'))
    num_pictures = glob.glob(
        os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER_PIC']))
    return render_template('start.html', last_visit=latest_file_time, overall_visits=num_files,
                           num_visits_today=num_filesToday, num_movies=num_pictures)


# Livestream für die Website
@app.route('/stream')
def stream_cam():
    return render_template('streaming.html')


# Route zum aufnehmen eines Videos direkt über die Website
@app.route('/capture')
def capture():
    # Define the codec and create VideoWriter object
    videoFolder = os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER_VID'])
    mHandler = Motion_Handler(vc=vc, vidHeigth=app.config['VID_RES_Y'], vidWidth=app.config['VID_RES_X'],
                              fileNamePrefix=app.config['LATEST_VID'], folder=videoFolder)
    mHandler.startRecording()
    return 'captured'


@app.route('/slideshow')
def slideshow():
    # Auslesen der Bilder im Applikationsverzeichnis und Anzeige auf der Webseite
    # die Konfiguration des Verzeichnisses erfolgt in der config.py

    pictures = []

    pic_path = os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER_PIC'])
    picturesList = list(sorted(pathlib.Path(pic_path).glob('*' + str(app.config['PIC_ENDING'])), key=os.path.getmtime))
    for pic in picturesList:
        pict = [pic.name, str(pic.relative_to(os.path.join(os.path.dirname(__file__), 'application')))]
        pictures.append(pict)
    return render_template('slideshow.html', pictures=pictures)


def gen():
    # """Video streaming generator function."""

    while True:
        read_return_code, frame = vc.read()
        if read_return_code:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
            _draw_label(frame, datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), (20, 20))

            encode_return_code, image_buffer = cv2.imencode(str(app.config['PIC_ENDING']), frame)
            io_buf = io.BytesIO(image_buffer)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')


def _draw_label(img, text, pos):
    # zeichnen des Labels in das Bild
    # das Bild die Position und der einzufügende Text werden als Parameter übergeben
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = .4
    color = (255, 255, 255)
    cv2.putText(img, text, pos, font_face, scale, color, 1, cv2.LINE_AA)


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/cam')
def cam():
    fileName_short = app.config['LATEST_PIC'] + datetime.datetime.now().strftime(app.config['TIME_FORMATE']) + str(
        app.config['PIC_ENDING'])
    full_web = os.path.join('static', app.config['UPLOAD_FOLDER_PIC'], fileName_short)
    full_filename = os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'],
                                 app.config['UPLOAD_FOLDER_PIC'],
                                 fileName_short)
    _take_picture(full_filename)
    return render_template('picture.html', picture=full_web)


# Aufnehmen eines Fotos
def _take_picture(fileName):
    read_return_code, frame = vc.read()

    _draw_label(frame, datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), (20, 20))
    if read_return_code:
        image_gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
        cv2.imwrite(fileName, image_gray)


# Liste von aufgezeichneten Bewegungen
@app.route('/activityList')
def activityList():
    activities = DBHandler(get_db()).getAllActivity()
    actList = activities.values.tolist()
    return render_template('ActivityList.html', activities=actList, report='/getlistxls')


# Export der Aktivitäten als Exceldatei
@app.route('/getlistxls')
def getAllItemsInWorkBook():
    activities = DBHandler(get_db()).getAllActivity()
    _cleanFolder(os.path.join(os.path.dirname(__file__), 'application', 'outputs'), app.config['ACTIVITY_LIST_OUT'])
    fileName = os.path.join('outputs', app.config['ACTIVITY_LIST_OUT'] +
                            datetime.datetime.now().strftime(app.config['TIME_FORMATE']) + app.config[
                                'ACTIVITY_LIST_END'])
    fileFullName = os.path.join(os.path.dirname(__file__), 'application', fileName)
    activities.to_excel(fileFullName, sheet_name=app.config['ACTIVITY_LIST_OUT'], index=False)

    return send_file(fileFullName,
                     mimetype='text/csv',
                     attachment_filename=fileFullName,
                     as_attachment=True)


@app.route('/videoList', methods=['GET', 'POST'])
def videoList():
    videos = []
    vidList = list()

    if request.method == 'POST':
        form_datum = request.form.get('dateFiles')
        sel_datum = datetime.datetime.strptime(form_datum, '%Y-%m-%d')
    else:
        sel_datum = datetime.datetime.today()

    vid_path = os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER_VID'])
    vidDate = str(sel_datum.day) + str(format(sel_datum.month, '02')) + str(
        sel_datum.year)
    for ending in app.config['VID_ENDINGS']:
        pattern = '*' + vidDate + ending
        vidList.extend(list(sorted(pathlib.Path(vid_path).glob(pattern), key=os.path.getmtime, reverse=True)))

    for media in vidList:
        vid = [media.name, str(media.relative_to(os.path.join(os.path.dirname(__file__), 'application')))]
        videos.append(vid)
    return render_template('videoshow.html', videos=videos, date_selection=sel_datum)


@app.route('/videoList_noDetect')
def videoList_noDetect():
    videos = []
    vidList = list()
    vid_path = os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER_VID_NO'])
    for ending in app.config['VID_ENDINGS']:
        vidList.extend(list(sorted(pathlib.Path(vid_path).glob(ending), key=os.path.getmtime)))

    for media in vidList:
        vid = [media.name, str(media.relative_to(os.path.join(os.path.dirname(__file__), 'application')))]
        videos.append(vid)
    return render_template('videoshow.html', videos=videos)


def _cleanFolder(folder, pattern):
    if os.path.exists(folder):
        for file_object in os.listdir(folder):
            file_object_path = os.path.join(folder, file_object)
            if file_object.startswith(pattern):
                if os.path.isfile(file_object_path) or os.path.islink(file_object_path):
                    os.unlink(file_object_path)
    else:
        os.makedirs(folder)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/climate')
def climate():
    climateRec = DBHandler().getAllClimateRecords()
    climateList = climateRec.values.tolist()
    climatePlot = climateRec

    if not climatePlot.empty:
        climatePlot.set_index('Datum')
        climatePlot.set_index('Zeit', append=True)['Temperatur'].plot(figsize=(12, 10), linewidth=2.5, color='maroon')

        chart = os.path.join(os.path.dirname(__file__), app.config['OUTPUT_FOLDER'], 'media', 'charts', 'climate.png')
        plt.title('Temperatur')
        plt.savefig(chart)
        chart_web = os.path.join(app.config['UPLOAD_FOLDER_CHART'], 'climate.png')
        return render_template('ClimateList.html', chart=chart_web, climateRec=climateList, report='/getclimatexls')
    else:
        return render_template('ClimateList.html', chart=None, climateRec=climateList, report='/getclimatexls')


@app.route('/getclimatexls')
def getclimatexls():
    climateRec = DBHandler().getAllClimateRecords()

    _cleanFolder(os.path.join(os.path.dirname(__file__), 'application', 'outputs'), 'Climate')

    fileName = os.path.join('outputs', 'Climate' + datetime.datetime.now().strftime(app.config['TIME_FORMATE'])
                            + app.config['ACTIVITY_LIST_END'])
    fileFullName = os.path.join(os.path.dirname(__file__), 'application', fileName)
    climateRec.to_excel(fileFullName, sheet_name='Climate', index=False)

    return send_file(fileFullName,
                     mimetype='text/csv',
                     attachment_filename=fileFullName,
                     as_attachment=True)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # sensitivity = request.form['sensitivity']

    return render_template("admin.html", enable_replay=True, inputSensitivity=100, replay_interval=10, dur_replay=7,
                           frames_per_sec_replay=30)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000')
