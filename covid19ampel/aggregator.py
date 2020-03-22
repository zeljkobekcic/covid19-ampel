import datetime as dt
import json
import os

import numpy as np
import pandas as pd
import psycopg2
import requests

from . import logistic as l


def clean_landkreis(value: str) -> str:
    if type(value) == float:
        return ""
    prefix = value[:2]
    first = value.split(" ")[0]
    if "Berlin" in value:
        return "Berlin"
    elif "Kreis" == first or "LK" == prefix or "SK" == prefix or "Region" == first or "Landkreis" == first or "Städteregion" == first or "StadtRegion" == first:
        return " ".join(value.split(" ")[1:])
    else:
        return value


def get_einwohner() -> pd.DataFrame:
    data_frame = pd.read_csv("../data/plz_einwohner.csv")
    data_frame.loc[:, "plz"] = data_frame.plz.apply(clean_zipcode)
    return data_frame.set_index("plz")[["einwohner"]]


def clean_zipcode(zipcode: int) -> str:
    return str(zipcode) if len(str(zipcode)) == 5 else "0" + str(zipcode)


def fill_empty_landkreis_with_ort(value):
    ort, landkreis = value
    return landkreis if landkreis not in [np.nan, ""] else ort


def get_landkreise() -> pd.DataFrame:
    data_frame = pd.read_csv("../data/zuordnung_plz_ort_landkreis.csv")
    data_frame.loc[:, "plz"] = data_frame.plz.apply(clean_zipcode)
    data_frame.loc[:, "Landkreis"] = data_frame["landkreis"].apply(clean_landkreis)
    data_frame.loc[:, "Landkreis"] = data_frame[["ort", "Landkreis"]].apply(fill_empty_landkreis_with_ort, axis=1)
    return data_frame.set_index("plz")[["Landkreis"]]


def get_cases() -> pd.DataFrame:
    url = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=1%3D1&objectIds=&time=&resultType=standard&outFields=Bundesland%2C+Landkreis%2C+Altersgruppe%2C+Geschlecht%2C+AnzahlFall%2C+AnzahlTodesfall%2C+Meldedatum&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=Landkreis&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="
    response = requests.get(url)
    text = json.loads(response.text)
    attributes = [x["attributes"] for x in text["features"]]
    data_frame = pd.DataFrame(attributes)
    data_frame.loc[:, "Landkreis"] = data_frame["Landkreis"].apply(clean_landkreis)
    data_frame.loc[:, "Meldedatum"] = data_frame["Meldedatum"].astype("datetime64[ms]")
    return data_frame


def main():
    cases = get_cases()
    infection_duration = dt.timedelta(days=14)
    today = dt.date.today()
    oldest_active = pd.Timestamp(today - infection_duration)
    active_cases = cases[cases["Meldedatum"] >= oldest_active].groupby("Landkreis").sum()
    immune_cases = cases[cases["Meldedatum"] < oldest_active].groupby("Landkreis").sum()
    first_case = cases.groupby("Landkreis")["Meldedatum"].min()

    zipcode_einwohner = get_einwohner()
    landkreise = get_landkreise()
    zipcodes = zipcode_einwohner.join(landkreise, on="plz", how="left", rsuffix="_landkreis")
    landkreis_einwohner = zipcodes.groupby("Landkreis").sum()["einwohner"].to_dict()

    result = zipcodes.join(active_cases, on="Landkreis", how="left")
    result.loc[:, "landkreis_einwohner"] = result["Landkreis"].map(landkreis_einwohner)
    result.loc[:, "Fälle pro 100K"] = 10 ** 5 * result["AnzahlFall"] / result["landkreis_einwohner"]
    result.loc[:, "Einträge rot"] = 0
    result.loc[:, "Einträge gelb"] = 0
    result.loc[:, "Einträge grün"] = 0

    prognose = {key: 0 for key in landkreis_einwohner.keys()}
    for landkreis, population in landkreis_einwohner.items():
        lk = cases[cases["Landkreis"] == landkreis]
        lk = lk.dropna(subset=["Meldedatum"])
        if len(lk) == 0:
            prognose[landkreis] = 0
            continue
        lk.loc[:, "days"] = (lk["Meldedatum"] - pd.to_datetime(today)).apply(lambda x: x.days)
        lk.loc[:, "days"] = abs(lk["days"].min()) + lk["days"]
        lk = lk.groupby("days").sum().expanding().sum()
        fallzahl = active_cases.loc[landkreis]["AnzahlFall"]
        if fallzahl < 50:
            prognose[landkreis] = 1.3 * fallzahl
        else:
            try:
                prognose[landkreis] = l.morgen(lk, population)
            except:
                prognose[landkreis] = 1.3 * fallzahl

    result.loc[:, "Prognose"] = result["Landkreis"].map(prognose)
    result.loc[:, "Wachstum"] = result["Prognose"] / result["AnzahlFall"]
    result.loc[:, "AnzahlImmun"] = result["Landkreis"].map(immune_cases["AnzahlFall"].to_dict()).replace(np.nan, 0)
    result.loc[:, "AnzahlAktiv"] = result["Landkreis"].map(active_cases["AnzahlFall"].to_dict()).replace(np.nan, 0)
    result.loc[:, "Erster Fall"] = result["Landkreis"].map(first_case.to_dict())

    con = psycopg2.connect(
        host=os.environ["PSQL_HOST"],
        dbname=os.environ["PSQL_DBNAME"],
        user=os.environ["PSQL_USER"],
        password=os.environ["PSQL_PASSWORD"],
    )
    db_write = (
        result
            .rename({
            "einwohner": "einwohner_plz",
            "Landkreis": "landkreis",
            "AnzahlAktiv": "anzahl_fall_aktiv_landkreis",
            "AnzahlImmun": "anzahl_fall_immun_landkreis",
            "AnzahlTodesfall": "anzahl_tode_landkreis",
            "landkreis_einwohner": "einwohner_landkreis",
            "Fälle pro 100K": "faelle_pro_hunderttausend",
            "Einträge rot": "eintrag_rot",
            "Einträge gelb": "eintrag_gelb",
            "Einträge grün": "eintrag_gruen",
            "Prognose": "prognose",
            "Wachstum": "wachstum",
            "Erster Fall": "erster_fall"
        })
            .drop("AnzahlFall")
            .to_sql(name="results", con=con)
    )
    result.to_csv("data/result.csv")


if __name__ == "__main__":
    main()
