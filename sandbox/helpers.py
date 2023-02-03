import psycopg2
import configparser

import sql_queries as qry


def get_api_key(api_name):
    """
    - return api key from configuration file
    """
    config = configparser.ConfigParser()
    config.read('./apis.cfg')

    return(config[api_name]['API_KEY'])


def db_connect():
    """
    - get db configuration
    - connect to database
    - return conn and cur objects
    """
    config = configparser.ConfigParser()
    config.read('./fireside.cfg')

    conn = psycopg2.connect(
        database=config['DB']['DB_NAME'],
        user=config['DB']['DB_USER'],
        password=config['DB']['DB_PASSWORD'],
        host=config['DB']['DB_HOST'],
    )

    conn.autocommit = True

    cur = conn.cursor()

    return conn, cur


def test_db_up(cur):
    """
    - create schemas (if not exist)
    - set search path to test schema
    - drop/create 'current' tables
    """
    # create the schemas
    cur.execute(qry.create_schemas)

    # only test against against the test schema
    cur.execute("SET search_path TO test,public;")

    # drop/create current tables
    cur.execute(qry.drop_current_tables)
    cur.execute(qry.create_current_tables)
