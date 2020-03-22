plz_shapefiles_url:="https://www.suche-postleitzahl.org/download_files/public/plz-gebiete.shp.zip"
einwohnerzahl_csv:="https://www.suche-postleitzahl.org/download_files/public/plz_einwohner.csv"
plz_landkreis_csv:="https://www.suche-postleitzahl.org/download_files/public/zuordnung_plz_ort_landkreis.csv"
target_directory:=/tmp/
target_shapefile:=/tmp/plz-gebiete.shp
sql_shapefile:=/tmp/plz-gebiete.sql
target_shapefile_zipped:=$(target_shapefile).zip

include .env
PSQL_ARGS = --host $(PSQL_HOST) --port $(PSQL_PORT) --user $(PSQL_USER) --dbname $(PSQL_DBNAME)

setup_shapefiles:
	# wget $(plz_shapefiles_url) --directory-prefix $(target_directory)
	unzip $(target_shapefile_zipped) -d $(target_directory)
	shp2pgsql -c -D -I -S -s 4326 $(sql_shapefile) plz_gebiete > $(sql_shapefile)
	PGPASSWORD=$(PSQL_PASSWORD) psql $(PSQL_ARGS) --file $(sql_shapefile)
	PGPASSWORD=$(PSQL_PASSWORD) psql $(PSQL_ARGS) --file database/setup.sql

setup_current_infected:
	mkdir -p data
	wget $(plz_landkreis_csv) --directory-prefix data/
	wget $(einwohnerzahl_csv) --directory-prefix data/

.env: .env.template
ifeq (,$(wildcard ./.env))
	cp .env.template .env
endif
