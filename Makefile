plz_shapefiles_url:="https://www.suche-postleitzahl.org/download_files/public/plz-gebiete.shp.zip"
target_directory=/tmp/
target_shapefile=/tmp/plz-gebiete.shp
sql_shapefile=/tmp/plz-gebiete.sql
target_shapefile_zipped=$(target_shapefile).zip

include .env
PSQL_ARGS = --host $(PSQL_HOST) --port $(PSQL_PORT) --user $(PSQL_USER) --dbname $(PSQL_DBNAME)

setup_shapefiles:
	mkdir -p $(cache_dir)
	wget $(plz_shapefiles_url) --directory-prefix $(target_directory)
	unzip $(cache_dir)/plz-gebiete.shp.zip -d $(cache_dir)
	shp2pgsql -c -D -I -S -s 4326 $(sql_shapefile) plz_gebiete > $(sql_shapefile)
	PGPASSWORD='zeljko' psql $(PSQL_ARGS) --file $(sql_shapefile)

.env: .env.template
ifeq (,$(wildcard ./.env))
	cp .env.template .env
endif
