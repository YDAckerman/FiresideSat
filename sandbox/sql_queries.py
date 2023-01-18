

create_schemas = """
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS current;
CREATE SCHEMA IF NOT EXISTS historic;
"""

drop_current_tables = """
DROP TABLE IF EXISTS current.incidents;
DROP TABLE IF EXISTS current.perimeters;
DROP TABLE IF EXISTS current.rings;
"""

create_current_tables = """
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
  incident_id varchar(256),
  ring_id integer NOT NULL,
  centroid_lat numeric(18,0),
  centroid_lon numeric(18,0)
);
"""

create_staging_tables = """
DROP TABLE IF EXISTS staging.incidents;
DROP TABLE IF EXISTS staging.perimeters;
DROP TABLE IF EXISTS staging.incidents_updated;
DROP TABLE IF EXISTS staging.incidents_outdated;

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

CREATE TABLE IF NOT EXISTS staging.incidents_updated(
    incident_id varchar(256) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS staging.incidents_outdated(
    incident_id varchar(256) PRIMARY KEY
);
"""

insert_updated_outdated = """
INSERT INTO staging.incidents_updated (incident_id)
SELECT si.incident_id AS incident_id
FROM staging.incidents si
LEFT JOIN current.incidents ci
ON si.incident_id = ci.incident_id
WHERE si.date_current > ci.date_current
OR ci.date_current IS NULL;

INSERT INTO staging.incidents_outdated (incident_id)
SELECT incident_id FROM current.incidents
WHERE current.incidents.incident_id NOT IN (
      SELECT incident_id FROM staging.incidents
);
"""

delete_all_outdated = """
DELETE FROM current.incidents
WHERE incident_id IN (SELECT incident_id FROM staging.incidents_outdated);
DELETE FROM current.perimeters
WHERE incident_id IN (SELECT incident_id FROM staging.incidents_outdated);
DELETE FROM current.rings
WHERE incident_id IN (SELECT incident_id FROM staging.incidents_outdated);
"""

upsert_current_incident = """
INSERT INTO current.incidents
SELECT * FROM staging.incidents
WHERE staging.incidents.incident_id IN
      (SELECT incident_id FROM staging.incidents_updated)
ON CONFLICT (incident_id) DO
UPDATE SET date_current      = EXCLUDED.date_current,
           centroid_lat      = EXCLUDED.centroid_lat,
           centroid_lon      = EXCLUDED.centroid_lon,
           behavior          = EXCLUDED.behavior,
           total_acres       = EXCLUDED.total_acres,
           percent_contained = EXCLUDED.percent_contained;
"""

upsert_current_perimeter = """
DELETE FROM current.perimeters
WHERE current.perimeters.incident_id IN
      (SELECT incident_id FROM staging.incidents_updated);
INSERT INTO current.perimeters
SELECT * FROM staging.perimeters
WHERE staging.perimeters.incident_id IN
      (SELECT incident_id FROM staging.incidents_updated);
"""

upsert_current_ring = """
DELETE FROM current.rings
WHERE current.rings.incident_id IN
      (SELECT incident_id FROM staging.incidents_updated);

INSERT INTO current.rings (incident_id, ring_id, centroid_lon, centroid_lat)
SELECT incident_id, ring_id, AVG(lon), AVG(lat)
FROM (
   SELECT * FROM current.perimeters WHERE incident_id IN (
        SELECT incident_id FROM staging.incidents_updated
   )
) as updated_perimeters
GROUP BY incident_id, ring_id;
"""

insert_staging_incident = """
INSERT INTO staging.incidents (incident_id, incident_name,
                               behavior, total_acres,
                               percent_contained, date_created,
                               date_current, centroid_lat,
                               centroid_lon)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

insert_staging_perimeter = """
INSERT INTO staging.perimeters (incident_id, ring_id, lon, lat)
VALUES %s
"""
