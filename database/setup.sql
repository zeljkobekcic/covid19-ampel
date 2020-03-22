-- plz,einwohner,Landkreis,AnzahlFall,AnzahlTodesfall,landkreis_einwohner,Fälle pro 100K,Einträge rot,Einträge gelb,Einträge grün,Prognose,Wachstum,AnzahlImmun,AnzahlAktiv,Erster Fall
create table results (
    plz VARCHAR(80) NOT NULL REFERENCES plz_gebiete(plz),
    einwohner INTEGER NOT NULL,
    landkreis VARCHAR(255) NOT NULL,
    anzhal_fall
)