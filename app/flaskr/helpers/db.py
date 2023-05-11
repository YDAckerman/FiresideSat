import psycopg2
import configparser
from flask import g


def get_conn():

    if 'conn' not in g:
        config = configparser.ConfigParser()
        config.read('./fireside.cfg')

        g.conn = psycopg2.connect(
            database=config['DB']['DB_NAME'],
            user=config['DB']['DB_USER'],
            password=config['DB']['DB_PASSWORD'],
            host=config['DB']['DB_HOST'],
            port=config['DB']['DB_PORT'],
        )

        return g.conn


def close_conn(e=None):
    conn = g.pop('conn', None)

    if conn is not None:
        conn.close()
