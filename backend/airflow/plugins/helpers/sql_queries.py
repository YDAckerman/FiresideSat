
class SqlQueries:

    drop_current_tables = """
    DROP TABLE IF EXISTS current_incidents;
    DROP TABLE IF EXISTS current_perimeters;
    DROP TABLE IF EXISTS current_aqi;
    """

    drop_user_table = """
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS devices;
    DROP TABLE IF EXISTS user_settings;
    """

    drop_trip_tables = """
    DROP TABLE IF EXISTS trips;
    DROP TABLE IF EXISTS trip_points;
    DROP TABLE IF EXISTS trip_points_aqi;
    """

    drop_report_tables = """
    DROP TABLE IF EXISTS incident_reports;
    DROP TABLE IF EXISTS trip_state_reports;
    DROP TABLE IF EXISTS user_aqi_reports;
    """

    drop_variables_table = """
    DROP TABLE IF EXISTS variables;
    """

    create_variables_table = """
    CREATE TABLE IF NOT EXISTS variables (
    name    varchar(256)   PRIMARY KEY,
    value   TEXT
    );
    """

    reset_public_key = """
    DELETE FROM variables WHERE name = 'rsa_public_key_pem';

    INSERT INTO variables (name, value)
    VALUES ('rsa_public_key_pem', %(pem)s);
    """

    create_report_tables = """
    CREATE TABLE IF NOT EXISTS incident_reports (
    user_id                integer        NOT NULL,
    incident_id            varchar(256)   NOT NULL,
    incident_last_update   timestamp      NOT NULL,
    aqi_last_update        timestamp      NOT NULL
    );

    CREATE TABLE IF NOT EXISTS trip_state_reports (
    user_id   integer    NOT NULL,
    trip_id   integer    NOT NULL,
    state     varchar    NOT NULL,
    date_sent timestamp  NOT NULL
    );

    CREATE TABLE IF NOT EXISTS user_aqi_reports (
    point_id    integer    NOT NULL,
    max_aqi     varchar    NOT NULL,
    min_aqi     varchar    NOT NULL,
    date_sent timestamp  NOT NULL
    );
    """

    insert_trip_state_report = """
    INSERT INTO trip_state_reports (user_id, trip_id,
                                    state, date_sent)
    VALUES (%(user_id)s, %(trip_id)s, %(state)s, %(date_sent)s);
    """

    insert_user_aqi_report = """
    INSERT INTO user_aqi_reports (point_id, max_aqi, min_aqi, date_sent)
    VALUES (%(point_id)s, %(max_aqi)s, %(min_aqi)s, %(aqi_date)s);
    """

    create_user_table = """
    CREATE TABLE IF NOT EXISTS users (
    user_id            serial         PRIMARY KEY,
    user_email         varchar(256),
    user_pw            varchar(256),
    mapshare_id        varchar(256)   UNIQUE NOT NULL,
    mapshare_pw        bytea          NOT NULL
    );

    CREATE TABLE IF NOT EXISTS devices (
    device_id          serial         PRIMARY KEY,
    user_id            integer        UNIQUE NOT NULL,
    garmin_imei        varchar(256),
    garmin_device_id   varchar(256)
    );

    CREATE TABLE IF NOT EXISTS user_settings (
    user_id            integer        NOT NULL,
    setting_name       varchar(256)   NOT NULL,
    setting_value      varchar(256)   NOT NULL
    );
    """

    create_trip_tables = """
    CREATE TABLE IF NOT EXISTS trips (
    trip_id            serial         PRIMARY KEY,
    user_id            integer        NOT NULL,
    device_id          integer        NOT NULL,
    start_date         timestamp      NOT NULL,
    end_date           timestamp      NOT NULL
    );

    CREATE TABLE IF NOT EXISTS trip_points (
    point_id           serial                   PRIMARY KEY,
    trip_id            integer                  NOT NULL,
    last_location      geometry(Point, 4326)    NOT NULL,
    course             varchar(256),
    date               timestamp                NOT NULL
    );

    CREATE TABLE IF NOT EXISTS trip_points_aqi (
    point_id    integer         NOT NULL,
    date        timestamp       NOT NULL,
    geom        geometry(Point, 4326),
    aqi         smallint        NOT NULL
    );
    """

    insert_incident_report = """
    INSERT INTO incident_reports (user_id,
                                  incident_id,
                                  incident_last_update,
                                  aqi_last_update)
    VALUES (%(user_id)s,
            %(incident_id)s,
            %(incident_last_update)s,
            %(aqi_last_update)s);
    """

    upsert_trip_points = """
    INSERT INTO trip_points (trip_id, last_location, course, date)
    SELECT s.trip_id, s.last_location, s.course, s.date
    FROM   staging_trip_points s LEFT JOIN trip_points t
    ON     s.trip_id = t.trip_id
    WHERE (s.date > t.date)
    -- AND NOT ST_Equals(s.last_location, t.last_location))
    OR     t.trip_id IS NULL;
    """

    create_staging_trip_points = """
    DROP TABLE IF EXISTS staging_trip_points;
    CREATE TABLE IF NOT EXISTS staging_trip_points (
    trip_id            serial         PRIMARY KEY,
    raw_lon            numeric        NOT NULL,
    raw_lat            numeric        NOT NULL,
    last_location geometry(Point, 4326) GENERATED ALWAYS AS (
         ST_SetSRID(ST_MakePoint(raw_lon, raw_lat), 4326)) STORED,
    course             varchar(256),
    date               timestamp      NOT NULL
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
    -- DROP TABLE IF EXISTS staging_incidents_outdated;

    CREATE TABLE IF NOT EXISTS staging_incidents (
    incident_id varchar(256) PRIMARY KEY,
    incident_name varchar(256),
    behavior varchar(256),
    total_acres integer,
    percent_contained smallint,
    date_created bigint NOT NULL,
    date_current bigint NOT NULL,
    raw_lon numeric NOT NULL,
    raw_lat numeric NOT NULL,
    centroid geometry(Point, 4326) GENERATED ALWAYS AS (
        ST_SetSRID(
                   ST_MakePoint(raw_lon, raw_lat),
                   4326
        )) STORED
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

    create_staging_aqi = """
    DROP TABLE IF EXISTS staging_aqi;
    CREATE TABLE IF NOT EXISTS staging_aqi (
           incident_id    varchar(256) NOT NULL,
           date           timestamp    NOT NULL,
           hour           smallint     NOT NULL,
           raw_lat        numeric      NOT NULL,
           raw_lon        numeric      NOT NULL,
           aqi            smallint     NOT NULL,
           geom   geometry(Point, 4326) GENERATED ALWAYS AS (
               ST_SetSRID(
                          ST_MakePoint(raw_lon, raw_lat),
                          4326
               )) STORED
    );
    """

    create_staging_trip_points_aqi = """
    DROP TABLE IF EXISTS staging_trip_points_aqi;
    CREATE TABLE IF NOT EXISTS staging_trip_points_aqi (
           point_id        integer      NOT NULL,
           date            timestamp    NOT NULL,
           hour            smallint     NOT NULL,
           raw_lat         numeric      NOT NULL,
           raw_lon         numeric      NOT NULL,
           aqi             smallint     NOT NULL,
           geom            geometry(Point, 4326) GENERATED ALWAYS AS (
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
    """

    upsert_current_incident = """
    INSERT INTO current_incidents
    SELECT incident_id, incident_name, centroid, date_created,
           date_current, behavior, total_acres, percent_contained
    FROM staging_incidents
    WHERE staging_incidents.incident_id IN
    (SELECT incident_id FROM staging_incidents_updated)
    AND total_acres IS NOT NULL
    ON CONFLICT (incident_id) DO
    UPDATE SET
    date_current      = EXCLUDED.date_current,
    centroid          = EXCLUDED.centroid,
    behavior          = EXCLUDED.behavior,
    total_acres       = EXCLUDED.total_acres,
    percent_contained = EXCLUDED.percent_contained;
    """

    upsert_current_aqi = """
    DELETE FROM current_aqi WHERE incident_id IN
    (SELECT DISTINCT incident_id FROM staging_aqi);
    INSERT INTO current_aqi
    SELECT incident_id, date, hour, geom, aqi
    FROM staging_aqi;
    """

    upsert_trip_points_aqi = """
    INSERT INTO trip_points_aqi
    SELECT point_id,
           date + ((hour)::varchar(256) || ' hour')::interval AS date,
           geom,
           aqi
    FROM staging_trip_points_aqi;
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

    select_current_incident_ids = """
    SELECT incident_id FROM current_incidents;
    """

    select_airnow_api_key = """
    SELECT value FROM variables
    WHERE name = 'airnow_api_key';
    """

    # this may no longer be necessary
    # I suppose I can calculate my own centroid based on
    # perimeter, but technically don't have to.
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

    select_fire_centroids = """
    SELECT incident_id,
           ST_X(centroid) as lon,
           ST_Y(centroid) as lat,
           35 as rad -- set this relative to the incident
    FROM current_incidents;
    """

    insert_staging_incident = """
    INSERT INTO staging_incidents (
                incident_id, incident_name,
                behavior, total_acres,
                percent_contained, date_created,
                date_current, raw_lon, raw_lat)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
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

    insert_staging_trip_points_aqi = """
    INSERT INTO staging_trip_points_aqi (point_id, date, hour,
                                         raw_lat, raw_lon, aqi)
    VALUES %s
    """

    insert_staging_trip_points = """
    INSERT INTO staging_trip_points (trip_id,
                                     date,
                                     raw_lon,
                                     raw_lat,
                                     course)
    VALUES (%s,%s,%s,%s,%s);
    """

    select_state_change_users = """
    SELECT users.user_id, users.mapshare_id, users.mapshare_pw,
           trips.trip_id, trips.start_date, trips.end_date,
           devices.garmin_device_id,
           CASE WHEN trips.start_date::date = (%(current_date)s)::date
                THEN 'Starting'::varchar(256)
                ELSE 'Stopping'::varchar(256)
           END
           AS state,
           (%(current_date)s)::date AS date_sent
    FROM   users
    JOIN   trips ON users.user_id = trips.user_id
    JOIN   devices ON trips.device_id = devices.device_id
    LEFT JOIN   trip_state_reports tsr ON users.user_id = tsr.user_id
    AND                              trips.trip_id = tsr.trip_id
    AND                              (trips.start_date = tsr.date_sent
    OR                                trips.end_date = tsr.date_sent)
    WHERE  (trips.start_date::date = (%(current_date)s)::date
    OR     trips.end_date::date = (%(current_date)s)::date)
    AND    (tsr.user_id IS NULL
    OR      tsr.trip_id IS NULL
    OR      tsr.date_sent IS NULL);
    """

    select_all_user_state_settings = """
    SELECT setting_value FROM user_settings
    WHERE setting_name = 'include_state';
    """

    select_active_users = """
    SELECT users.user_id, trip_id, garmin_imei,
                          mapshare_id, mapshare_pw
    FROM   users
    JOIN   trips ON users.user_id = trips.user_id
    JOIN   devices ON trips.device_id = devices.device_id
    WHERE  trips.start_date <= %(current_date)s
    AND    trips.end_date >= %(current_date)s;
    """

    select_latest_points = """
    SELECT tp.point_id,
           ST_X(last_location) as lon,
           ST_Y(last_location) as lat,
           35 as rad
    FROM (
          SELECT tp.*, row_number() OVER (PARTITION BY trip_id
                                          ORDER BY date DESC
                                         ) AS row_num
          FROM trip_points tp
         ) tp
    JOIN trips t ON tp.trip_id = t.trip_id
    WHERE row_num = 1
    AND   t.start_date <= %(current_date)s
    AND   t.end_date >= %(current_date)s;
    """

    select_active_users_latest_aqi = """

    DROP TABLE IF EXISTS latest_points;
    CREATE TEMP TABLE latest_points AS
    SELECT t.user_id, t.trip_id, tp.point_id
    FROM (
          -- seems like I could have just taken max(date) here...
          SELECT tp.*, row_number() OVER (PARTITION BY trip_id
                                          ORDER BY date DESC
                                         ) AS row_num
          FROM trip_points tp
         ) tp
    JOIN trips t ON tp.trip_id = t.trip_id
    WHERE row_num = 1
    AND   t.start_date <= %(current_date)s
    AND   t.end_date >= %(current_date)s;

    DROP TABLE IF EXISTS latest_points_aqi;
    CREATE TEMP TABLE latest_points_aqi AS
    SELECT lp.user_id, lp.trip_id, lp.point_id,
           MAX(tpa.aqi) AS max_aqi, MIN(tpa.aqi) AS min_aqi,
           MAX(tpa.date) AS aqi_date
    FROM latest_points lp
    JOIN (
          -- there are multiple rows of aqi data for each
          -- point, so we don't want to partition like above.
          SELECT tpa1.point_id, tpa1.aqi, tpa1.date
          FROM trip_points_aqi tpa1
          JOIN (
                SELECT point_id, MAX(date) AS max_date
                FROM trip_points_aqi
                GROUP BY point_id
                ) tpa2
          ON  tpa1.point_id = tpa2.point_id
          AND tpa1.date = tpa2.max_date
    ) tpa
    ON lp.point_id = tpa.point_id
    GROUP BY lp.user_id,
             lp.trip_id,
             lp.point_id;

    SELECT u.user_id,
           lpa.point_id,
           u.mapshare_id,
           u.mapshare_pw,
           d.garmin_device_id,
           lpa.max_aqi,
           lpa.min_aqi,
           lpa.aqi_date
    FROM latest_points_aqi lpa
    JOIN users u ON  lpa.user_id = u.user_id
    JOIN devices d ON lpa.user_id = d.user_id;
    """

    # NOTE: THE DATE BOUNDS NEED TO BE CHANGED!!!
    select_user_incidents = """
    DROP TABLE IF EXISTS user_incidents;
    CREATE TEMP TABLE user_incidents AS
    SELECT active_trips.user_id,
           ci.incident_id,
           to_timestamp(ci.date_current / 1000) AS incident_last_update,
           ca.aqi_date AS aqi_last_update,
           CASE WHEN ci.total_acres::varchar = ''
                THEN '?'
                ELSE ci.total_acres::varchar
           END
           AS total_acres,
           ci.behavior AS incident_behavior,
           ci.incident_name,
           round(ST_Distance(latest_points.last_location::geography,
                       ci.centroid::geography)::numeric, 2) AS dist_m_to_center,
           round(ST_X(ST_Transform(ci.centroid, 4326))::numeric, 4) AS
           centroid_lon,
           round(ST_Y(ST_Transform(ci.centroid, 4326))::numeric, 4) AS
           centroid_lat,
           ca.max_aqi,
           ST_X(ST_Transform(ca.geom, 4326)) AS aqi_obs_lon,
           ST_Y(ST_Transform(ca.geom, 4326)) AS aqi_obs_lat
    FROM   (SELECT *
            FROM trips
            WHERE trips.start_date <= %(current_date)s
            AND   trips.end_date >= %(current_date)s
           ) active_trips
    JOIN   (SELECT t1.last_location,
                   t1.trip_id,
                   t2.last_update
            FROM trip_points t1
            JOIN (SELECT trip_id,
                         MAX(date) AS last_update
                  FROM trip_points
                    GROUP BY trip_id) t2
            ON t1.trip_id = t2.trip_id
            AND t1.date = t2.last_update
           ) latest_points
    ON   active_trips.trip_id = latest_points.trip_id
    JOIN (SELECT user_id, setting_value::numeric AS alert_radius
          FROM user_settings
          WHERE setting_name = 'alert_radius_meters'
         ) usr_rules
    ON active_trips.user_id = usr_rules.user_id
    -- total_acres should never be null...
    JOIN (SELECT * FROM current_incidents WHERE total_acres IS NOT NULL) ci
    ON   ST_DWithin(latest_points.last_location::geography,
                    ci.centroid::geography,
                    usr_rules.alert_radius)
    JOIN (
          SELECT c1.incident_id, c1.geom,
                 c1.date + ((c1.hour)::varchar(256) || ' hour')::interval
                 AS aqi_date,
                 c2.max_aqi
          FROM current_aqi c1
          JOIN (
                SELECT incident_id, MAX(aqi) AS max_aqi
                FROM current_aqi
                GROUP BY incident_id) c2
          ON c1.incident_id = c2.incident_id
          AND c1.aqi = c2.max_aqi
    ) ca
    ON ci.incident_id = ca.incident_id;

    -- CREATE TEMP TABLE incident_filter AS
    -- SELECT user_id, incident_id
    -- FROM user_incidents
    -- ORDER BY max_aqi DESC
    -- LIMIT 1;

    DROP TABLE IF EXISTS user_messages;
    CREATE TEMP TABLE user_messages AS
    SELECT DISTINCT ui.*, u.mapshare_id, u.mapshare_pw, d.garmin_device_id
    FROM user_incidents ui
    LEFT JOIN incident_reports ir
    ON   ui.user_id = ir.user_id
    AND  ui.incident_id = ir.incident_id
    AND  ui.incident_last_update <= ir.incident_last_update
    JOIN users u ON ui.user_id = u.user_id
    JOIN devices d ON ui.user_id = d.user_id
    WHERE (ir.user_id IS NULL)
    OR     (ui.aqi_last_update >= (ir.aqi_last_update
                                        + interval '12 hour'));

    -- Limit the number of messages.
    SELECT um.*
    FROM (SELECT um.*,
                 row_number() OVER (PARTITION BY user_id
                                    ORDER BY incident_last_update DESC,
                                             total_acres DESC NULLS LAST,
                                             max_aqi DESC NULLS LAST
                                   ) AS row_num
          FROM user_messages um) um
    WHERE row_num <= 2;
    """
