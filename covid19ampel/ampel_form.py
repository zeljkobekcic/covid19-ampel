import os
import psycopg2
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, ValidationError
from wtforms.validators import InputRequired, Length
from . import app


class PostcodeValidator:
    def __init__(self, message=None):

        if 'DATABASE_URL' in os.environ:
            DATABASE_URL = os.environ['DATABASE_URL']
        elif 'DATABASE_URL' in app.config:
            DATABASE_URL = app.config['DATABASE_URL']
        else:
            raise Exception("Could not load database credentials")

        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        except psycopg2.OperationalError:
            conn = psycopg2.connect(DATABASE_URL)

        else:
            raise Exception("No database credentials configured!")



        if message is None:
            self.message = "postcode has not been found"
        else:
            self.message = message

        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT plz FROM plz_gebiete;")
            self.postcodes = [p[0] for p in cur.fetchall()]

    def __call__(self, form, field):
        if field.data not in self.postcodes:
            raise ValidationError(self.message)


class AmpelForm(FlaskForm):
    postcode = StringField(
        "Meine Postleitzahl",
        validators=[
            InputRequired(
                "Das Postleitzahlfeld ist notwendig um fortzufahren"),
            PostcodeValidator("Bitte eine gültige Postleitzahl eingeben"),
        ],
    )
    ampel = RadioField(
        "Ampel",
        choices=[
            ("red", "Mir wurde bestätigt, den Corona Virus zu haben."),
            (
                "yellow",
                """
                Ich fühle mich krank und habe mindestens eines der folgenden 
                Symptome: Fieber, Husten, Kurzatmigkeit oder Halsschmerzen. 
                Weitere Symptome können auch Muskel- /Gelenkschmerzen, 
                Kopfschmerzen, Übelkeit/Erbrechen, eine verstopfte Nase oder 
                Durchfall sein.
                """,
            ),
            (
                "green",
                """
                Ich fühle mich gesund und hatte seit mindestens 2 Wochen keinen
                Kontakt zu einem bestätigten Corona-Patienten.
                """,
            ),
        ],
        validators=[InputRequired("Bitte geben Sie ein wie es Ihnen geht")]
    )
    submit = SubmitField("Weiter")
