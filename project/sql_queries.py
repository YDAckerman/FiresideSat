# SQL QUERIES


# Drop Table Queries

drop_users_table = "DROP TABLE IF EXISTS users"

# drop_trips_table = "DROP TABLE IF EXISTS trips"

# drop_points_table = "DROP TABLE IF EXISTS points"

drop_time_table = "DROP TABLE IF EXISTS time"

drop_fires_table = "DROP TABLE IF EXISTS fires"


# Create Table Queries

create_users_table = """
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_code TEXT NOT NULL,
current_password TEXT NOT NULL,
active BOOLEAN NOT NULL
)
"""

# create_trips_table = """
# CREATE TABLE IF NOT EXISTS trips (
# trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
# start_time_id INTEGER NOT NULL,
# end_time_id INTEGER
# )
# """

# create_points_table = """
# CREATE TABLE IF NOT EXISTS points (
# point_id INTEGER PRIMARY KEY AUTOINCREMENT,
# user_id INTEGER NOT NULL,
# time_id INTEGER NOT NULL,
# long FLOAT NOT NULL,
# lat FLOAT NOT NULL
# )
# """

create_fires_table = """
CREATE TABLE IF NOT EXISTS fires (
fire_id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
start_time_id INTEGER NOT NULL,
acres FLOAT NOT NULL,
containment INTEGER NOT NULL
)
"""

create_time_table = """
CREATE TABLE IF NOT EXISTS time (
time_id INTEGER PRIMARY KEY AUTOINCREMENT,
year INTEGER NOT NULL,
month INTEGER NOT NULL,
day INTEGER NOT NULL
)
"""


drop_table_queries = [drop_users_table,
                      drop_trips_table,
                      drop_points_table,
                      drop_fires_table,
                      drop_time_table]

create_table_queries = [create_users_table,
                        create_trips_table,
                        create_points_table,
                        create_fires_table,
                        create_time_table]
