import psycopg2
import json
from . import app
import random
from pprint import pprint
import os

from flask import render_template


@app.route('/by/postcode/<postcode>', methods=['GET'])
def get_postcode_center(postcode: str):
    conn = psycopg2.connect(
        host=os.environ['PSQL_HOST'],
        dbname=os.environ['PSQL_DBNAME'],
        user=os.environ['PSQL_USER'],
        password=os.environ['PSQL_PASSWORD']
    )
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT ST_AsGeoJson(plz_gebiete.geom), plz_gebiete.plz
            FROM plz_gebiete
            WHERE ST_INTERSECTS(
                geom,
                (
                    SELECT plz_gebiete.geom
                    FROM plz_gebiete
                    WHERE plz_gebiete.plz = '41460'
                    LIMIT 1
                )
            );
            """,
            {'postcode': postcode}
        )

        def cur_iterator():
            row = cur.fetchone()
            while row is not None:
                yield row
                row = cur.fetchone()

        geojsons = [
            {
                'type': 'Feature',
                'properties': {
                    'danger': random.randint(0, 100),
                    'postcode': postcode
                },
                'geometry': json.loads(geom)
            }
            for geom, postcode, *_ in cur_iterator()
        ]


    return render_template('index.html',geojsons=geojsons)

