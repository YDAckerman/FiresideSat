-- DEPRECATED see ../helpers/sql_queries

-- DROP TABLE IF EXISTS current_incidents;
-- DROP TABLE IF EXISTS current_perimeters;
-- DROP TABLE IF EXISTS current_bounding_boxes;
-- DROP TABLE IF EXISTS current_aqi;

-- CREATE TABLE IF NOT EXISTS current_incidents (
--     incident_id        varchar(256)   PRIMARY KEY,
--     incident_name      varchar(256),
--     centroid_lat       numeric(18,0),
--     centroid_lon       numeric(18,0),
--     date_created       bigint         NOT NULL,
--     date_current       bigint         NOT NULL,
--     behavior           varchar(256),
--     total_acres        integer,
--     percent_contained  smallint
-- );

-- CREATE TABLE IF NOT EXISTS current_perimeters (
--     incident_id        varchar(256)   NOT NULL,
--     ring_id            integer        NOT NULL,
--     lon                numeric(18,0),
--     lat                numeric(18,0)
-- );

-- CREATE TABLE IF NOT EXISTS current_bounding_boxes (
--     incident_id        varchar(256),
--     centroid_lat       numeric(18,0),
--     centroid_lon       numeric(18,0),
--     bbox_max_lat       numeric(18,0),
--     bbox_min_lat       numeric(18,0),
--     bbox_max_lon       numeric(18,0),
--     bbox_min_lon       numeric(18,0)
-- );

-- CREATE TABLE IF NOT EXISTS current_aqi (
--     incident_id        varchar(256),
--     obs_date           timestamp      NOT NULL,
--     obs_lat            numeric(18,0),
--     obs_lon            numeric(18,0),
--     obs_aqi            smallint
-- );

-- CREATE TABLE IF NOT EXISTS users (
--     user_id            serial         PRIMARY KEY,
--     user_email         varchar(256),
--     user_otp           varchar(256),
--     has_active_trip    boolean
-- )

-- CREATE TABLE IF NOT EXISTS trips (
--     trip_id            serial         PRIMARY KEY,
--     trip_pw            varchar(256),
--     user_id            integer,
--     active             boolean,
--     last_location      geometry(Point, 4326),
--     last_update        timestamp
-- )
