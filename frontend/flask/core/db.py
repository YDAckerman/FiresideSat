
import psycopg2
from psycopg2.extras import execute_values
from flask import current_app, g
from .result import RESULT_DB_ERR


def get_conn():
    if 'conn' not in g:

        g.conn = psycopg2.connect(
            database=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
        )

    return g.conn


def db_extract(query, data):
    conn = get_conn()
    with conn.cursor() as cur:
        try:
            cur.execute(query, data)
        except Exception as e:
            print(e)
            return None
        return cur.fetchall()


def db_submit(query, data, res):
    conn = get_conn()
    with conn.cursor() as cur:
        try:
            cur.execute(query, data)
        except Exception as e:
            print(e)
            return RESULT_DB_ERR
    conn.commit()
    return res


def db_submit_many(query, data, res):
    conn = get_conn()
    with conn.cursor() as cur:
        try:
            execute_values(cur, query, data)
        except Exception as e:
            print(e)
            return RESULT_DB_ERR
    conn.commit()
    return res


def close_conn(e=None):
    conn = g.pop('conn', None)

    if conn is not None:
        conn.close()


def init_app(app):
    app.teardown_appcontext(close_conn)
