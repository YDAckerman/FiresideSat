
class SqlQueries:

    # probably should have a safer separation of
    # test and prod? For now I won't be using them.
    create_schemas = """
    CREATE SCHEMA IF NOT EXISTS dev;
    CREATE SCHEMA IF NOT EXISTS test;
    """

    drop_current_tables = """
    DROP TABLE IF EXISTS current_incidents;
    DROP TABLE IF EXISTS current_perimeters;
    DROP TABLE IF EXISTS current_aqi;
    """

    drop_user_table = """
    DROP TABLE IF EXISTS users;
    """

    drop_device_table = """
    DROP TABLE IF EXISTS devices;
    """

    drop_trip_tables = """
    DROP TABLE IF EXISTS trips;
    DROP TABLE IF EXISTS trip_points;
    DROP TABLE IF EXISTS staging_trip_points;
    """

    create_user_table = """
    CREATE TABLE IF NOT EXISTS users (
    user_id            serial         PRIMARY KEY,
    user_email         varchar(256)   NOT NULL,
    user_otp           varchar(256)   NOT NULL,
    mapshare_id        varchar(256)
    );
    """

    create_device_table = """
    CREATE TABLE IF NOT EXISTS devices (
    device_id          serial         PRIMARY KEY,
    user_id            integer        NOT NULL,
    garmin_device_id   integer        NOT NULL
    );
    """

    create_trip_tables = """
    CREATE TABLE IF NOT EXISTS trips (
    trip_id            serial         PRIMARY KEY,
    trip_pw            varchar(256),
    user_id            integer        NOT NULL,
    device_id          integer        NOT NULL,
    start_date         timestamp      NOT NULL,
    end_date           timestamp      NOT NULL
    );

    CREATE TABLE IF NOT EXISTS trip_points (
    point_id           serial                   PRIMARY KEY,
    trip_id            integer                  NOT NULL,
    last_location      geometry(Point, 4326)    NOT NULL,
    last_update        timestamp                NOT NULL
    );

    CREATE TABLE IF NOT EXISTS staging_trip_points (
    trip_id            serial         PRIMARY KEY,
    raw_lon            numeric        NOT NULL,
    raw_lat            numeric        NOT NULL,
    last_location geometry(Point, 4326) GENERATED ALWAYS AS (
         ST_SetSRID(ST_MakePoint(raw_lon, raw_lat), 4326)) STORED,
    last_update        timestamp      NOT NULL
    );
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
    geom geometry(Point, 4326),
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
           incident_id    varchar(256),
           date           timestamp   NOT NULL,
           hour           smallint    NOT NULL,
           raw_lat        numeric     NOT NULL,
           raw_lon        numeric     NOT NULL,
           aqi            smallint    NOT NULL,
           geom   geometry(Point, 4326) GENERATED ALWAYS AS (
               ST_SetSRID(
                          ST_MakePoint(raw_lon, raw_lat),
                          4326
               )) STORED
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

    # We want to remove aqi values from incidents that are no longer
    # active. Also, remove all but the most recent aqi values
    # for each incident
    delete_aqi_outdated = """
    DELETE FROM current_aqi
    WHERE incident_id IN (SELECT incident_id FROM staging_incidents_outdated);
    DELETE FROM current_aqi ca1
    WHERE EXISTS (
          SELECT *
          FROM current_aqi ca2
          WHERE ca2.incident_id = ca1.incident_id
          AND ca2.date >= ca1.date
          AND ca2.hour > ca1.hour
    );
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

    # These values are based on geom from current_incidents
    upsert_current_aqi = """
    INSERT INTO current_aqi
    SELECT incident_id, date, hour, geom, aqi FROM staging_aqi;
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

    insert_staging_aqi = """
    INSERT INTO staging_aqi (incident_id, date, hour,
                             raw_lat, raw_lon, aqi)
    VALUES %s
    """
