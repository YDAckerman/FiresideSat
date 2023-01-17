

create_schemas_query = """
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS current;
CREATE SCHEMA IF NOT EXISTS historic;
"""

create_current_tables_query = """
CREATE TABLE IF NOT EXISTS current.incidents (
   incident_id varchar(256) PRIMARY KEY,
   incident_name varchar(256),
   centroid_lat numeric(18,0),
   centroid_lon numeric(18,0),
   date_created timestamp NOT NULL,
   date_current timestamp NOT NULL,
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
DROP TABLE IF EXISTS staging.incidents;
DROP TABLE IF EXISTS staging.perimeters;
CREATE TABLE IF NOT EXISTS staging.incidents (
   incident_id varchar(256) PRIMARY KEY,
   incident_name varchar(256),
   centroid_lat numeric(18,0),
   centroid_lon numeric(18,0),
   date_created timestamp NOT NULL,
   date_current timestamp NOT NULL,
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

create_updated_outdated_query = """
CREATE TEMPORARY TABLE staging.incidents_updated(
    incident_id varchar(256) PRIMARY KEY,
);
INSERT INTO staging.incidents_updated VALUES (
    SELECT incident_id FROM staging.incidents
    WHERE staging.incidents.incident_id NOT IN current.incidents.incident_id
          OR (staging.incidents.incident_id = current.incidents.incident_id
          AND staging.incidents.date_current > current.incidents.date_current)
);

CREATE TEMPORARY TABLE staging.incidents_outdated(
    incident_id varchar(256) PRIMARY KEY,
);
INSERT INTO staging.incidents_outdated VALUES (
    SELECT incident_id FROM current.incidents
    WHERE current.incidents.incident_id NOT IN staging.incidents.incident_id
);
"""

delete_all_outdated_query = """
DELETE FROM current.incidents
WHERE incident_id IN staging.incidents_outdated.incident_id;
DELETE FROM current.perimeters
WHERE incident_id IN staging.incidents_outdated.incident_id;
DELETE FROM current.rings
WHERE incident_id IN staging.incidents_outdated.incident_id;
"""

upsert_current_incident_query = """
INSERT INTO staging.incidents (incident_id, incident_name,
                                behavior, total_acres,
                                percent_contained, date_created,
                                date_current, centroid_lat,
                                centroid_lon)
VALUES (
    SELECT * FROM staging.incidents
    WHERE staging.incidents.incident_id IN
          staging.incidents_updated.incident_id
)
ON CONFLICT (incident_id) DO
UPDATE SET date_current      = EXCLUDED.date_current,
           centroid_lat      = EXCLUDED.centroid_lat,
           centroid_lon      = EXCLUDED.centroid_lon,
           behavior          = EXCLUDED.behavior,
           total_acres       = EXCLUDED.total_acres,
           percent_contained = EXCLUDED.percent_contained;
"""

upsert_current_perimeter_query = """
DELETE FROM current.perimeters
WHERE current.perimeters.incident_id IN staging.incidents_updated.incident_id;
INSERT INTO current.perimeters (incident_id, ring_id, lon, lat)
VALUES (
    SELECT * FROM staging.perimeters
    WHERE staging.perimeters.incident_id IN
          staging.incidents_updated.incident_id
);
"""

upsert_current_ring_query = """
DELETE FROM current.rings
WHERE current.rings.incident_id IN staging.incidents_updated.incident_id;
INSERT INTO current.rings (incident_id, ring_id, centroid_lon, centroid_lat)
VALUES (
    SELECT incident_id, ring_id, MEAN(lon), MEAN(lat) FROM
    current.perimeters
);

"""

insert_staging_incident_query = """
INSERT INTO staging.incidents (incident_id, incident_name,
                                  behavior, total_acres,
                                  percent_contained, date_created,
                                  date_current, centroid_lat,
                                  centroid_lon)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

insert_staging_perimeter_query = """
INSERT INTO staging.perimeters (incident_id, ring_id, lon, lat)
VALUES %s
"""
