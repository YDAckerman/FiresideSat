
-- Create incident Table

CREATE TABLE IF NOT EXISTS incidents (
       incident_id varchar(256) PRIMARY KEY,
       incident_name varchar(256),
       centroid_lat numeric(18,0),
       centroid_lon numeric(18,0),
       date_create timestamp NOT NULL,
       date_current timestamp NOT NULL,
       behavior varchar(256),
       total_acres integer,
       percent_contained smallint
);

-- Create perimeters table

CREATE TABLE IF NOT EXISTS perimeters (
      incident_id varchar(256) PRIMARY KEY,
      ring_id varchar(256) NOT NULL,
      lon numeric(18,0),
      lat numeric(18,0)
);
