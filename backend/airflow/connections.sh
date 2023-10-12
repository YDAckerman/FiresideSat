#!/bin/sh

# Connections
airflow connections add 'fireside' \
        --conn-type 'postgres' \
        --conn-host 'fireside' \
        --conn-schema 'fireside' \
        --conn-login 'root' \
        --conn-password 'secret' \
        --conn-port 5432

airflow connections add 'fireside_prod' \
        --conn-type 'postgres' \
        --conn-host 'fireside_prod' \
        --conn-schema 'fireside' \
        --conn-login 'root' \
        --conn-password 'secret' \
        --conn-port 5432

airflow connections add 'wildfire_api' \
        --conn-type 'http' \
        --conn-host 'https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/'

airflow connections add 'airnow' \
        --conn-type 'http' \
        --conn-host 'https://www.airnowapi.org/aq/observation/latLong/current/'

airflow connections add 'mapshare_feed' \
        --conn-type 'http' \
        --conn-host 'https://explore.garmin.com/feed/share/'
 
airflow connections add 'garmin_share' \
        --conn-type 'http' \
        --conn-host 'https://share.garmin.com/'

echo 'connections added' 


