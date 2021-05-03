import datetime
import glob
import io
import os
import pathlib
import sqlite3
import threading
import time

from application.forms.admin_form import AdminForm
from application.handler.database_hndl import DBHandler

try:
    from uwsgidecorators import *
    import uwsgi
except:
    pass
import cv2
import matplotlib.pyplot as plt
from flask import render_template, Response, send_file, g, request, redirect, url_for

from application.handler.motion_handler import Motion_Handler
from application.handler.screen_shoot_handler import ScreenShotHandler
from application import create_app, updateSetup, constants

app = create_app()

# Erzeugen der Instanz für die Aufnahme
#
# da die Kamera für die Aufnahe für andere Programme dann gesperrt ist
# ist es erforderlich die Instanz an die weiteren Funktionen weiterzugeben
vc = cv2.VideoCapture(0)
app.config[constants.VIDEO_CAPTURE_INST] = vc
vc.set(cv2.CAP_PROP_FPS, int(app.config[constants.VID_FRAMES]))
vc.set(cv2.CAP_PROP_FRAME_WIDTH, int(app.config[constants.VID_RES_X]))
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, int(app.config[constants.VID_RES_Y]))
vc.set(cv2.CAP_PROP_BUFFERSIZE, 3)
videoFolder = os.path.join(app.root_path, app.config[constants.OUTPUT_FOLDER], app.config[constants.UPLOAD_FOLDER_VID])
pictureFolder = os.path.join(app.root_path, app.config[constants.OUTPUT_FOLDER],
                             app.config[constants.UPLOAD_FOLDER_PIC])
replayFolder = os.path.join(app.root_path, app.config[constants.OUTPUT_FOLDER],
                            app.config[constants.UPLOAD_FOLDER_REPLAY])
DATABASE = app.config[constants.SQLALCHEMY_DATABASE_URI]


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def create_BG_task():
    thread = threading.Thread(target=uwsgi_task)
    thread.start()


def uwsgi_task():
    Motion_Handler(app=app).detect()
    ScreenShotHandler().startTread()


# Erzeugen eines Hintergrundtask, welcher die Kamera permanent überwacht und be Bewegungen eine Aufzeichnung startet
create_BG_task()


@app.route('/')
@app.route('/personas', methods=['GET', 'POST'])
def personas():
    _db = DBHandler(app.config[constants.SQLALCHEMY_DATABASE_URI])
    if request.method == 'GET':

        first_visit = app.config[constants.FIRST_VISIT]
        date_eggs = app.config[constants.DATE_EGG]
        date_chick = app.config[constants.DATE_CHICK]
        date_leave = app.config[constants.DATE_LEAVE]
        name_bird = app.config[constants.NAME_BIRD]

    elif request.method == 'POST':
        name_bird = request.form['name_bird']
        first_visit = request.form['first_visit']
        date_eggs = request.form['date_eggs']
        date_chick = request.form['date_chick']
        date_leave = request.form['date_leave']

        if name_bird is not None or name_bird is not '':
            _db.createUpdateConfigEntry(constants.NEST_CONFIG, constants.NAME_BIRD, name_bird)
        if first_visit is not None or first_visit is not '':
            _db.createUpdateConfigEntry(constants.NEST_CONFIG, constants.FIRST_VISIT, first_visit)
        if date_eggs is not None or date_eggs is not '':
            _db.createUpdateConfigEntry(constants.NEST_CONFIG, constants.DATE_EGG, date_eggs)
        if date_chick is not None or date_chick is not '':
            _db.createUpdateConfigEntry(constants.NEST_CONFIG, constants.DATE_CHICK, date_chick)
        if date_leave is not None or date_leave is not '':
            _db.createUpdateConfigEntry(constants.NEST_CONFIG, constants.DATE_LEAVE, date_leave)
    folder_personas = os.path.join(app.root_path, app.config[constants.OUTPUT_FOLDER],
                                   app.config[constants.UPLOAD_FOLDER_PERSONAS]) + '/personas' + str(
        app.config[constants.ENDING_PIC])
    pic_personas = str(
        pathlib.Path(folder_personas).relative_to(app.root_path))
    latest_file_time = ''
    videoFolder = os.path.join(os.path.dirname(__file__), app.config[constants.OUTPUT_FOLDER],
                               app.config[constants.UPLOAD_FOLDER_VID])
    list_of_files = glob.glob(videoFolder + '/*' + app.config[constants.VID_FORMAT])
    num_filesToday = len(glob.glob(videoFolder + '/*' + str(datetime.datetime.today().day) + str(
        format(datetime.datetime.today().month, '02')) + str(datetime.datetime.today().year) + '*' + app.config[
                                       constants.VID_FORMAT]))
    if len(list_of_files) > 0 and list_of_files is not None:
        latest_file = max(list_of_files, key=os.path.getctime)
        latest_file_time = time.strftime(constants.DATETIME_FORMATE_UI, time.localtime(os.stat(latest_file).st_ctime))
    return render_template("personas.html", num_visits_today=num_filesToday, last_visit=latest_file_time,
                           pic_personas=pic_personas, first_visit=first_visit, date_eggs=date_eggs,
                           date_chick=date_chick, date_leave=date_leave, name_bird=name_bird)


# Livestream für die Website
@app.route('/stream')
def stream_cam():
    return render_template('streaming.html')


# Route zum aufnehmen eines Videos direkt über die Website
@app.route('/capture')
def capture():
    # Define the codec and create VideoWriter object
    mHandler = Motion_Handler(app=app)
    mHandler.startRecording()
    return redirect(url_for('slideshow'))


@app.route('/slideshow')
def slideshow():
    # Auslesen der Bilder im Applikationsverzeichnis und Anzeige auf der Webseite
    # die Konfiguration des Verzeichnisses erfolgt in der config.py

    pictures = []

    pic_path = os.path.join(app.root_path, app.config[constants.OUTPUT_FOLDER], app.config[constants.UPLOAD_FOLDER_PIC])
    picturesList = list(
        sorted(pathlib.Path(pic_path).glob('*' + str(app.config[constants.ENDING_PIC])), key=os.path.getmtime))
    for pic in picturesList:
        pict = [pic.name, str(pic.relative_to(app.root_path))]
        pictures.append(pict)
    return render_template('slideshow.html', pictures=pictures)


def gen():
    # """Video streaming generator function."""

    while True:
        read_return_code, frame = vc.read()
        if read_return_code:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
            _draw_label(frame, datetime.datetime.now().strftime(constants.DATETIME_FORMAT), (20, 20))

            encode_return_code, image_buffer = cv2.imencode('.' + str(app.config[constants.ENDING_PIC]), frame)
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
    fileName_short = app.config[constants.PREFIX_PIC] + datetime.datetime.now().strftime(
        app.config[constants.TIME_FORMAT_FILE]) + str(
        app.config[constants.ENDING_PIC])
    full_web = os.path.join(app.config[constants.OUTPUT_FOLDER], app.config[constants.UPLOAD_FOLDER_PIC],
                            fileName_short)
    full_filename = os.path.join(app.root_path, app.config[constants.OUTPUT_FOLDER],
                                 app.config[constants.UPLOAD_FOLDER_PIC],
                                 fileName_short)
    _take_picture(full_filename)
    return redirect(url_for('slideshow'))


# Aufnehmen eines Fotos
def _take_picture(fileName):
    read_return_code, frame = vc.read()

    _draw_label(frame, datetime.datetime.now().strftime(constants.DATETIME_FORMAT), (20, 20))
    if read_return_code:
        image_gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
        cv2.imwrite(fileName, image_gray)


# Liste von aufgezeichneten Bewegungen
@app.route('/activityList')
def activityList():
    activities = DBHandler(app.config[constants.SQLALCHEMY_DATABASE_URI]).getAllActivity()
    actList = activities.values.tolist()
    return render_template('ActivityList.html', activities=actList, report='/getlistxls')


# Export der Aktivitäten als Exceldatei
@app.route('/getlistxls')
def getAllItemsInWorkBook():
    activities = DBHandler(app.config[constants.SQLALCHEMY_DATABASE_URI]).getAllActivity()
    _cleanFolder(os.path.join(app.root_path, app.config[constants.FOLDER_CSV_FILE_OUTPUT]),
                 app.config[constants.ACTIVITY_LIST_OUT])
    fileName = os.path.join(app.config[constants.FOLDER_CSV_FILE_OUTPUT], app.config[constants.ACTIVITY_LIST_OUT] +
                            datetime.datetime.now().strftime(app.config[constants.TIME_FORMAT_FILE]) + app.config[
                                constants.ACTIVITY_LIST_END])
    fileFullName = os.path.join(app.root_path, fileName)
    activities.to_excel(fileFullName, sheet_name=app.config[constants.ACTIVITY_LIST_OUT], index=False)

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
        sel_datum = datetime.datetime.strptime(form_datum, constants.DATEFORMATE_FILE_SEL)
    else:
        sel_datum = datetime.datetime.today()

    vid_path = os.path.join(os.path.dirname(__file__), app.config[constants.OUTPUT_FOLDER],
                            app.config[constants.UPLOAD_FOLDER_VID])
    vidDate = str(sel_datum.day) + str(format(sel_datum.month, '02')) + str(
        sel_datum.year)
    for ending in app.config[constants.VID_ENDINGS]:
        pattern = '*' + vidDate + ending
        vidList.extend(list(sorted(pathlib.Path(vid_path).glob(pattern), key=os.path.getmtime, reverse=True)))

    for media in vidList:
        vid = [media.name, str(media.relative_to(app.root_path))]
        videos.append(vid)
    return render_template('videoshow.html', videos=videos, date_selection=sel_datum)


@app.route('/videoList_noDetect')
def videoList_noDetect():
    videos = []
    vidList = list()
    vid_path = os.path.join(os.path.dirname(__file__), app.config[constants.OUTPUT_FOLDER],
                            app.config[constants.UPLOAD_FOLDER_VID_NO])
    for ending in app.config[constants.VID_ENDINGS]:
        vidList.extend(list(sorted(pathlib.Path(vid_path).glob(ending), key=os.path.getmtime)))

    for media in vidList:
        vid = [media.name, str(media.relative_to(app.root_path))]
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
    climateRec = DBHandler(app.config[constants.SQLALCHEMY_DATABASE_URI]).getAllClimateRecords()
    climateList = climateRec.values.tolist()
    climatePlot = climateRec

    if not climatePlot.empty:
        climatePlot.set_index('Datum')
        climatePlot.set_index('Zeit', append=True)['Temperatur'].plot(figsize=(12, 10), linewidth=2.5, color='maroon')

        chart = os.path.join(os.path.dirname(__file__), app.config[constants.OUTPUT_FOLDER], 'media', 'charts',
                             'climate.png')
        plt.title('Temperatur')
        plt.savefig(chart)
        chart_web = os.path.join(app.config[constants.UPLOAD_FOLDER_CHART], 'climate.png')
        return render_template('ClimateList.html', chart=chart_web, climateRec=climateList, report='/getclimatexls')
    else:
        return render_template('ClimateList.html', chart=None, climateRec=climateList, report='/getclimatexls')


@app.route('/getclimatexls')
def getclimatexls():
    climateRec = DBHandler(app.config[constants.SQLALCHEMY_DATABASE_URI]).getAllClimateRecords()

    _cleanFolder(os.path.join(app.root_path, app.config[constants.FOLDER_CSV_FILE_OUTPUT]), 'Climate')

    fileName = os.path.join(app.config[constants.FOLDER_CSV_FILE_OUTPUT],
                            'Climate' + datetime.datetime.now().strftime(app.config[constants.TIME_FORMAT])
                            + app.config[constants.ACTIVITY_LIST_END])
    fileName = os.path.join('outputs',
                            'Climate' + datetime.datetime.now().strftime(app.config[constants.DATETIME_FORMAT])
                            + app.config['ACTIVITY_LIST_END'])
    fileFullName = os.path.join(os.path.dirname(__file__), 'application', fileName)
    climateRec.to_excel(fileFullName, sheet_name='Climate', index=False)

    return send_file(fileFullName,
                     mimetype='text/csv',
                     attachment_filename=fileFullName,
                     as_attachment=True)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    adminForm = AdminForm()
    if request.method == 'POST':
        appConfig = [
            [constants.DURATION_VID, 'duration_vid', 'int'],
            [constants.VID_RES_X, 'vid_res_x', 'int'],
            [constants.VID_RES_Y, 'vid_res_y', 'int'],
            [constants.SENSITIVITY, 'sensitivity', 'int'],
            [constants.PREFIX_VID, 'prefix_vid', 'str'],
            [constants.REPLAY_ENABLED, 'replay_enabled', 'bool'],
            [constants.REPLAY_INTERVAL, 'replay_interval', 'int'],
            [constants.FRAMES_PER_SEC_REPLAY, 'frames_per_sec_replay', 'int'],
            [constants.REPLAY_DAYS, 'replay_days', 'int'],
            [constants.SERVER_UPLOAD_ENABLED, 'upload_enabled', 'bool'],
            [constants.NUM_RETRY_UPLOAD, 'num_retry_upload', 'int'],
            [constants.PAUSE_RETRY_UPLOAD, 'pause_retry_upload', 'int'],
            [constants.SERVER_UPLOAD, 'server_upload', 'str'],
            [constants.FOLDER_UPLOAD, 'folder_upload', 'str'],
            [constants.TIME_UPLOAD, 'time_upload', 'date'],
            [constants.ENDING_PIC, 'pic_ending', 'str'],
            [constants.PREFIX_PIC, 'prefix_pic', 'str']
        ]

        for appConfigEntry in appConfig:

            if appConfigEntry[0][-8:] == '_ENABLED' and request.form.get(appConfigEntry[1]) is None:
                app.config[appConfigEntry[0]] = False
            elif appConfigEntry[0][-8:] == '_ENABLED' and request.form.get(appConfigEntry[1]) is not None:
                app.config[appConfigEntry[0]] = True
            else:
                if request.form.get(appConfigEntry[1]) is not None and appConfigEntry[2] is not 'int':
                    app.config[appConfigEntry[0]] = request.form.get(appConfigEntry[1])
                elif request.form.get(appConfigEntry[1]) is not None and appConfigEntry[2] is 'int':
                    app.config[appConfigEntry[0]] = int(float(request.form.get(appConfigEntry[1])))
                else:
                    continue
        updateSetup(_app=app)

    if app.config[constants.DURATION_VID] is None:
        adminForm.duration_vid.data = int(0)
        adminForm.duration_vidVal.data = int(0)
    else:
        adminForm.duration_vid.data = int(float(app.config[constants.DURATION_VID]))
        adminForm.duration_vidVal.data = int(float(app.config[constants.DURATION_VID]))
    if app.config[constants.VID_RES_X] is None:
        adminForm.vid_res_x.data = int(0)
    else:
        adminForm.vid_res_x.data = int(app.config[constants.VID_RES_X])
    if app.config[constants.VID_RES_Y] is None:
        adminForm.vid_res_y.data = int(0)
    else:
        adminForm.vid_res_y.data = int(app.config[constants.VID_RES_Y])
    if app.config[constants.SENSITIVITY] is None:
        adminForm.sensitivity.data = int(0)
        adminForm.sensitivityVal.data = int(0)
    else:
        adminForm.sensitivity.data = int(float(app.config[constants.SENSITIVITY]))
        adminForm.sensitivityVal.data = int(float(app.config[constants.SENSITIVITY]))
    if app.config[constants.REPLAY_INTERVAL] is None:
        adminForm.replay_interval.data = int(0)
    else:
        adminForm.replay_interval.data = int(app.config[constants.REPLAY_INTERVAL])
    if app.config[constants.REPLAY_DAYS] is None:
        adminForm.replay_days.data = int(0)
    else:
        adminForm.replay_days.data = int(app.config[constants.REPLAY_DAYS])
    if app.config[constants.FRAMES_PER_SEC_REPLAY] is None:
        adminForm.frames_per_sec_replay.data = int(0)
    else:
        adminForm.frames_per_sec_replay.data = int(app.config[constants.FRAMES_PER_SEC_REPLAY])
    if app.config[constants.NUM_RETRY_UPLOAD] is None:
        adminForm.num_retry_upload.data = int(0)
    else:
        adminForm.num_retry_upload.data = int(app.config[constants.NUM_RETRY_UPLOAD])

    if app.config[constants.PAUSE_RETRY_UPLOAD] is None:
        adminForm.pause_retry_upload.data = int(0)
    else:
        adminForm.pause_retry_upload.data = int(app.config[constants.PAUSE_RETRY_UPLOAD])

    adminForm.prefix_vid.data = app.config[constants.PREFIX_VID]

    if app.config[constants.REPLAY_ENABLED]:
        adminForm.replay_enabled.data = True
    else:
        adminForm.replay_enabled.data = False

    if app.config[constants.SERVER_UPLOAD_ENABLED]:
        adminForm.upload_enabled.data = True
    else:
        adminForm.upload_enabled.data = False

    adminForm.server_upload.data = app.config[constants.SERVER_UPLOAD]
    adminForm.folder_upload.data = app.config[constants.FOLDER_UPLOAD]
    adminForm.time_upload.data = datetime.datetime.strptime(app.config[constants.TIME_UPLOAD],
                                                            constants.UPLOAD_TIME_FORMAT).time()

    adminForm.prefix_pic.data = app.config[constants.PREFIX_PIC]
    adminForm.pic_ending.data = app.config[constants.ENDING_PIC]

    if adminForm.validate_on_submit():
        return redirect(url_for("admin"))
    return render_template(
        "admin_new.html",
        form=adminForm,
        template="form-template"
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)
