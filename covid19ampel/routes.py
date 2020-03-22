import psycopg2
import json
from . import app
from .ampel_form import AmpelForm
import random
import os

from flask import render_template, request, redirect


@app.route("/", methods=["GET", "POST"])
def get_landing_page():
    form = AmpelForm()

    if request.method == "POST" and form.validate_on_submit():
        print(form.postcode.data)
        print(form.ampel.data)
        print(form.postcode.errors)
        print(form.ampel.errors)
        redirect("/postcodemap")

    return render_template("index.html", form=form)


@app.route("/postcodemap", methods=["POST"])
def get_postcode_center():
    form = AmpelForm()

    if not form.validate_on_submit():
        print(form.postcode.data)
        print(form.ampel.data)
        print(form.postcode.errors)
        print(form.ampel.errors)
        return redirect("/")

    conn = psycopg2.connect(
        host=os.environ["PSQL_HOST"],
        dbname=os.environ["PSQL_DBNAME"],
        user=os.environ["PSQL_USER"],
        password=os.environ["PSQL_PASSWORD"],
    )
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 
                ST_AsGeoJson(plz_gebiete.geom) :: json, 
                ST_AsGeoJson(ST_Centroid(plz_gebiete.geom)) :: json,
                plz_gebiete.plz
            FROM plz_gebiete
            WHERE ST_INTERSECTS(
                geom,
                (
                    SELECT plz_gebiete.geom
                    FROM plz_gebiete
                    WHERE plz_gebiete.plz = %(postcode)s
                    LIMIT 1
                )
            );
            """,
            {"postcode": form.postcode.data},
        )

        rows = cur.fetchall()
        geojsons = [
            {
                "type": "Feature",
                "properties": {
                    "danger_min": 0,
                    "danger_max": 100,
                    "danger": random.randint(0, 100),
                    "postcode": postcode,
                },
                "geometry": geom,
            }
            for geom, _, postcode, *_ in rows
        ]

        center = None
        for row in rows:
            if row[2] == form.postcode.data:
                center = [row[1]["coordinates"][1], row[1]["coordinates"][0]]

    return render_template("map.html", geojsons=geojsons, center=center)
