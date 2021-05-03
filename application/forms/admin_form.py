from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    BooleanField,
    SubmitField,
    SelectField,

)
from wtforms.fields.html5 import (
    TimeField,
    IntegerField,
    DecimalRangeField
)
from wtforms.validators import (
    DataRequired,
    URL
)


class AdminForm(FlaskForm):
    style = {'class': 'adminFormOutputField', 'disabled': 'disabled"', 'style': 'border:0'}
    """Admin Bereich für Nistkasten"""
    duration_vid = DecimalRangeField(
        'Dauer der Videoaufnahme in s', [
            DataRequired()
        ],
        default=15
    )
    duration_vidVal = IntegerField(
        '', render_kw=style
    )
    vid_res_x = IntegerField(
        'Video X', render_kw=style

    )
    vid_res_y = IntegerField(
        'Video Y', render_kw=style
    )
    sensitivity = DecimalRangeField(
        'Empflindlichkeit', default=3000

    )
    sensitivityVal = IntegerField(
        '', render_kw=style

    )
    prefix_vid = StringField(
        'Videoprefix',
        [
            DataRequired(message="Please enter a prefix for the video naming.")
        ]
    )
    replay_enabled = BooleanField(
        'automatische Aufnahmen'
    )
    replay_interval = IntegerField(
        'Intervall Einzelbilder in Minuten'
    )
    replay_days = IntegerField(
        'Zeitraum für Zeitraffer'
    )
    frames_per_sec_replay = IntegerField(
        'Bilder je sec Zeitraffer'
    )
    upload_enabled = BooleanField(
        'Serverupload'
    )
    num_retry_upload = IntegerField(
        'Anzahl Versuche Upload'
    )
    pause_retry_upload = IntegerField(
        'Anzahl Versuche Upload bei Nichterreichbarkeit in Minuten'
    )
    server_upload = StringField(
        'Server für Upload'
    )
    folder_upload = StringField(
        'Verzeichnis für Upload'
    )
    time_upload = TimeField(
        'Zeitpunkt für Upload'
    )
    prefix_pic = StringField(
        'Prefix für Bilder'
    )
    days_replay = IntegerField(
        'Zeitraum für Zeitraffer in Tagen'
    )
    pic_ending = SelectField(
        'Endung der Bilder',
        [DataRequired()],
        choices=[
            ('jpg', '.jpg')
        ]
    )

    website = StringField(
        'Website',
        validators=[URL()]
    )
    submit = SubmitField('Submit')
