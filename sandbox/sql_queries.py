

create_schemas = """
CREATE SCHEMA IF NOT EXISTS prod;
CREATE SCHEMA IF NOT EXISTS test;
"""

drop_current_tables = """
DROP TABLE IF EXISTS current_incidents;
DROP TABLE IF EXISTS current_perimeters;
DROP TABLE IF EXISTS current_rings;
"""

create_current_tables = """
CREATE TABLE IF NOT EXISTS current_incidents (
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

CREATE TABLE IF NOT EXISTS current_perimeters (
  incident_id varchar(256) NOT NULL,
  ring_id integer NOT NULL,
  lon numeric(18,0),
  lat numeric(18,0)
);

CREATE TABLE IF NOT EXISTS current_rings (
  incident_id varchar(256),
  ring_id integer NOT NULL,
  centroid_lat numeric(18,0),
  centroid_lon numeric(18,0)
);
"""

create_staging_tables = """
DROP TABLE IF EXISTS staging_incidents;
DROP TABLE IF EXISTS staging_perimeters;
DROP TABLE IF EXISTS staging_incidents_updated;
DROP TABLE IF EXISTS staging_incidents_outdated;

CREATE TABLE IF NOT EXISTS staging_incidents (
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

CREATE TABLE IF NOT EXISTS staging_perimeters (
  incident_id varchar(256) NOT NULL,
  ring_id integer NOT NULL,
  lon numeric(18,0),
  lat numeric(18,0)
);

CREATE TABLE IF NOT EXISTS staging_incidents_updated(
    incident_id varchar(256) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS staging_incidents_outdated(
    incident_id varchar(256) PRIMARY KEY
);
"""

insert_updated_outdated = """
INSERT INTO staging_incidents_updated (incident_id)
SELECT si.incident_id AS incident_id
FROM staging_incidents si
LEFT JOIN current_incidents ci
ON si.incident_id = ci.incident_id
WHERE si.date_current > ci.date_current
OR ci.date_current IS NULL;

INSERT INTO staging_incidents_outdated (incident_id)
SELECT incident_id FROM current_incidents
WHERE current_incidents.incident_id NOT IN (
      SELECT incident_id FROM staging_incidents
);
"""

delete_all_outdated = """
DELETE FROM current_incidents
WHERE incident_id IN (SELECT incident_id FROM staging_incidents_outdated);
DELETE FROM current_perimeters
WHERE incident_id IN (SELECT incident_id FROM staging_incidents_outdated);
DELETE FROM current_rings
WHERE incident_id IN (SELECT incident_id FROM staging_incidents_outdated);
"""

upsert_current_incident = """
INSERT INTO current_incidents
SELECT * FROM staging_incidents
WHERE staging_incidents.incident_id IN
      (SELECT incident_id FROM staging_incidents_updated)
ON CONFLICT (incident_id) DO
UPDATE SET date_current      = EXCLUDED.date_current,
           centroid_lat      = EXCLUDED.centroid_lat,
           centroid_lon      = EXCLUDED.centroid_lon,
           behavior          = EXCLUDED.behavior,
           total_acres       = EXCLUDED.total_acres,
           percent_contained = EXCLUDED.percent_contained;
"""

upsert_current_perimeter = """
DELETE FROM current_perimeters
WHERE current_perimeters.incident_id IN
      (SELECT incident_id FROM staging_incidents_updated);
INSERT INTO current_perimeters
SELECT * FROM staging_perimeters
WHERE staging_perimeters.incident_id IN
      (SELECT incident_id FROM staging_incidents_updated);
"""

upsert_current_ring = """
DELETE FROM current_rings
WHERE current_rings.incident_id IN
      (SELECT incident_id FROM staging_incidents_updated);

INSERT INTO current_rings (incident_id, ring_id, centroid_lon, centroid_lat)
SELECT incident_id, ring_id, AVG(lon), AVG(lat)
FROM (
   SELECT * FROM current_perimeters WHERE incident_id IN (
        SELECT incident_id FROM staging_incidents_updated
   )
) as updated_perimeters
GROUP BY incident_id, ring_id;
"""

insert_staging_incident = """
INSERT INTO staging_incidents (incident_id, incident_name,
                               behavior, total_acres,
                               percent_contained, date_created,
                               date_current, centroid_lat,
                               centroid_lon)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

insert_staging_perimeter = """
INSERT INTO staging_perimeters (incident_id, ring_id, lon, lat)
VALUES %s
"""
