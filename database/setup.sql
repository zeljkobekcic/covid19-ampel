create table results (
    plz_gid INTEGER NOT NULL REFERENCES plz_gebiete(gid),
    einwohner_plz INTEGER NOT NULL,
    landkreis VARCHAR(255) NOT NULL,
    anzahl_fall_aktiv_landkreis INTEGER NOT NULL,
    anzahl_fall_immun_landkreis INTEGER NOT NULL,
    anzahl_tode_landkreis INTEGER,
    einwohner_landkreis INTEGER NOT NULL,
    faelle_pro_hunderttausend FLOAT,
    eintrag_rot INTEGER NOT NULL,
    eintrag_gelb INTEGER NOT NULL,
    eintrag_gruen INTEGER NOT NULL,
    prognose INTEGER NOT NULL,
    wachstum FLOAT,
    erster_fall TIMESTAMP
)