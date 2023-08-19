
import psycopg2
from flask import current_app, g


def get_conn():
    if 'db' not in g:

        g.conn = psycopg2.connect(
            database=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
        )

    return g.conn


def close_conn(e=None):
    conn = g.pop('conn', None)

    if conn is not None:
        conn.close()
