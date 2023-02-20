

class SqlQueries:

    create_schemas = """
    CREATE SCHEMA IF NOT EXISTS prod;
    CREATE SCHEMA IF NOT EXISTS test;
    """

    drop_current_tables = """
    DROP TABLE IF EXISTS current_incidents;
    DROP TABLE IF EXISTS current_perimeters;
    DROP TABLE IF EXISTS current_aqi;
    """

    create_current_tables = """
    CREATE TABLE IF NOT EXISTS current_incidents (
    incident_id varchar(256) PRIMARY KEY,
    incident_name varchar(256),
    centroid geometry(Point, 4326),
    date_created bigint NOT NULL,
    date_current bigint NOT NULL,
    behavior varchar(256),
    total_acres integer,
    percent_contained smallint
    );

    CREATE TABLE IF NOT EXISTS current_perimeters (
    incident_id varchar(256) NOT NULL,
    ring_id integer NOT NULL,
    geom geometry(Point, 4326)
    );

    CREATE TABLE IF NOT EXISTS current_aqi (
    incident_id varchar(256),
    date timestamp NOT NULL,
    hour smallint NOT NULL,
    geom geometry(Point, 4326) GENERATED ALWAYS AS (
        ST_SetSRID(
                   ST_MakePoint(obs_lon, obs_lat),
                   4326
        )) STORED
    ),
    aqi smallint
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
    centroid geometry(Point, 4326),
    date_created bigint NOT NULL,
    date_current bigint NOT NULL,
    behavior varchar(256),
    total_acres integer,
    percent_contained smallint
    );

    CREATE TABLE IF NOT EXISTS staging_perimeters (
    incident_id varchar(256) NOT NULL,
    ring_id integer NOT NULL,
    raw_lon numeric NOT NULL,
    raw_lat numeric NOT NULL,
    geom geometry(Point, 4326) GENERATED ALWAYS AS (
        ST_SetSRID(
                   ST_MakePoint(raw_lon, raw_lat),
                   4326
        )) STORED
    );

    CREATE TABLE IF NOT EXISTS staging_incidents_updated(
    incident_id varchar(256) PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS staging_incidents_outdated(
    incident_id varchar(256) PRIMARY KEY
    );
    """

    # TODO: create aqi_dag
    create_staging_aqi = """
    DROP TABLE IF EXISTS staging_aqi;
    CREATE TABLE IF NOT EXISTS staging_aqi (
    incident_id varchar(256),
    date timestamp NOT NULL,
    hour smallint NOT NULL,
    geom geometry(Point, 4326) GENERATED ALWAYS AS (
        ST_SetSRID(
                   ST_MakePoint(raw_lon, raw_lat),
                   4326
        )) STORED
    ),
    raw_lat numeric,
    raw_lon numeric,
    aqi     smallint
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
    """

    # TODO: create aqi_dag
    delete_aqi_outdated = """
    DELETE FROM current_aqi
    WHERE incident_id IN (SELECT incident_id FROM staging_incidents_outdated);
    """

    upsert_current_incident = """
    INSERT INTO current_incidents
    SELECT * FROM staging_incidents
    WHERE staging_incidents.incident_id IN
    (SELECT incident_id FROM staging_incidents_updated)
    ON CONFLICT (incident_id) DO
    UPDATE SET
    date_current      = EXCLUDED.date_current,
    centroid          = EXCLUDED.centroid,
    behavior          = EXCLUDED.behavior,
    total_acres       = EXCLUDED.total_acres,
    percent_contained = EXCLUDED.percent_contained;
    """

    # TODO: create aqi_dag
    upsert_current_aqi = """
    INSERT INTO current_aqi
    SELECT * FROM staging_aqi
    WHERE stating_aqi.incident_id IN
    (SELEcT incident_id FROM staging_incidents_updated)
    ON CONFLICT (incident_id) DO
    UPDATE SET
    date = EXCLUDED.date,
    hour = EXCLUDED.hour,
    geom = EXCLUDED.geom,
    aqi  = EXCLUDED.aqi;
    """

    upsert_current_perimeter = """
    DELETE FROM current_perimeters
    WHERE current_perimeters.incident_id IN
    (SELECT incident_id FROM staging_incidents_updated);

    INSERT INTO current_perimeters
    SELECT incident_id, ring_id, geom FROM staging_perimeters
    WHERE staging_perimeters.incident_id IN
    (SELECT incident_id FROM staging_incidents_updated);
    """

    upsert_staging_centroids = """
    UPDATE staging_incidents SET
                   centroid = pc.centroid
    FROM (
      SELECT incident_id, ST_GeometricMedian(geom) AS centroid
      FROM (SELECT incident_id,
                   ST_Multi(ST_Union(geom))::geometry(MultiPoint, 4326)
                   AS geom
            FROM staging_perimeters
            GROUP BY incident_id
            ) pc1
    ) pc
    WHERE pc.incident_id = staging_incidents.incident_id;
    """

    select_bounding_boxes = """
    SELECT incident_id, bbox_min_lon,
           bbox_min_lat, bbox_max_lon, bbox_max_lat,
    FROM current_bounding_boxes;
    """

    # TODO: create aqi_dag
    select_centroids = """
    SELECT incident_id,
           ST_X(centroid) as lon,
           ST_Y(centroid) as lat
    FROM current_incidents;
    """

    insert_staging_incident = """
    INSERT INTO staging_incidents (
                incident_id, incident_name,
                behavior, total_acres,
                percent_contained, date_created,
                date_current, centroid)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
    """

    insert_staging_perimeter = """
    INSERT INTO staging_perimeters (incident_id, ring_id,
                                    raw_lon, raw_lat)
    VALUES %s
    """

    # TODO: create aqi_dag
    insert_staging_aqi = """
    INSERT INTO staging_perimeters (incident_id, date, hour,
                                    raw_lat, raw_lon, aqi)
    VALUES %s
    """
