

create_schemas_query = """
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS current;
CREATE SCHEMA IF NOT EXISTS historic;
"""


drop_staging_tables_query = """
DROP TABLE IF EXISTS staging.incidents;
DROP TABLE IF EXISTS staging.perimeters;
"""


create_current_tables_query = """
CREATE TABLE IF NOT EXISTS current.incidents (
   incident_id varchar(256) PRIMARY KEY,
   incident_name varchar(256),
   centroid_lat numeric(18,0),
   centroid_lon numeric(18,0),
   date_created timestamp NOT NULL,
   date_last_update timestamp NOT NULL,
   behavior varchar(256),
   total_acres integer,
   percent_contained smallint
);

CREATE TABLE IF NOT EXISTS current.perimeters (
  incident_id varchar(256) NOT NULL,
  ring_id integer NOT NULL,
  lon numeric(18,0),
  lat numeric(18,0)
);

CREATE TABLE IF NOT EXISTS current.rings (
  incident_id varchar(256) PRIMARY KEY,
  ring_id integer NOT NULL,
  centroid_lat numeric(18,0),
  centroid_lon numeric(18,0)
);
"""

create_staging_tables_query = """
CREATE TABLE IF NOT EXISTS staging.incidents (
   incident_id varchar(256) PRIMARY KEY,
   incident_name varchar(256),
   centroid_lat numeric(18,0),
   centroid_lon numeric(18,0),
   date_created timestamp NOT NULL,
   date_last_update timestamp NOT NULL,
   behavior varchar(256),
   total_acres integer,
   percent_contained smallint
);

CREATE TABLE IF NOT EXISTS staging.perimeters (
  incident_id varchar(256) NOT NULL,
  ring_id integer NOT NULL,
  lon numeric(18,0),
  lat numeric(18,0)
);
"""

insert_current_incident_query = """
INSERT INTO staging.incidents (incident_id, incident_name,
                                  behavior, total_acres,
                                  percent_contained, date_created,
                                  date_last_update, centroid_lat,
                                  centroid_lon)
VALUES (SELECT * FROM staging.incidents)
ON CONFLICT (incident_id) DO
UPDATE SET date_last_update  = EXCLUDED.date_last_update,
           centroid_lat      = EXCLUDED.centroid_lat,
           centroid_lon      = EXCLUDED.centroid_lon,
           behavior          = EXCLUDED.behavior,
           total_acres       = EXCLUDED.total_acres,
           percent_contained = EXCLUDED.percent_contained;
"""

insert_staging_incident_query = """
INSERT INTO staging.incidents (incident_id, incident_name,
                                  behavior, total_acres,
                                  percent_contained, date_created,
                                  date_last_update, centroid_lat,
                                  centroid_lon)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

delete_staging_perimeter_query = """
DELETE FROM staging.perimeters
WHERE incident_id = %s;
"""

insert_staging_perimeter_query = """
INSERT INTO staging.perimeters (incident_id, ring_id, lon, lat)
VALUES %s
"""
