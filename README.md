# Covid19 Ampel 🚦

# Setup

Get the code:
```shell script
git clone git@github.com:zeljkobekcic/covid19-ampel.git 
cd covid19-ampel
```
`
install the needed packages, if needed also the development packages:
```shell script
pipenv install
pipenv install --dev
```

Setup a postgresql database with postgist. The postgresql setup is for 
development purposes only and should be hardened before applying on for 
production.

Install postgresql and postgist (example for debian based systems)
```shell script
sudo apt install postgresql postgis 
sudo su postgres
psql
```

In your postgresql shell connection now do the following to create:
- a database
- a user with permissions to access it
- install the postgis extension

```postgresql
create database DATABASE_NAME_IN_HERE;  
create user YOUR_USERNAME_IN_HERE with password 'YOUR_PASSWORD_IN_HERE';
grant all privileges on database DATABASE_NAME_IN_HERE to YOUR_USERNAME_IN_HERE;

\connect DATABASE_NAME_IN_HERE>

CREATE EXTENSION postgis;
SELECT postgis_full_version(); -- check if postgis has been installed successfully
```

Create the enviroment variable file from the template and configure it 
according to the previous changes with your given `EDITOR` variable or nano if 
it is not set. You may use any other editor as well

```shell script
make .env
${EDITOR:-nano} .env
```

Populate the database with the shapefiles of the german postcodes with the 
following:

```shell script
make setup_shapefiles
pipenv run flask run -- finally run the application
```
