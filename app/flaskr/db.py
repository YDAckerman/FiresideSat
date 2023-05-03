import psycopg2
import configparser
import random

import click
from flask import current_app, g
from flask.cli import with_appcontext

OTP_LEN = 6
OTP_LOWER, OTP_UPPER = (0, 9)


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


def delete_user(cur, user_email):
    cur.execute("""
                DELETE FROM users
                WHERE user_email = %(user_email)s
                """, {
                    'user_email': user_email
                })


def create_user(cur, user_email):
    # otp should certainly go elsewhere.
    # this is just development
    otp = ''.join([str(random.randint(OTP_LOWER,
                                      OTP_UPPER))
                   for _ in range(OTP_LEN)])
    cur.execute("""
                INSERT INTO users (user_email,
                                   user_otp,
                                   has_active_trip)
                VALUES (%(user_email)s,
                        %(user_otp)s,
                        %(user_trips)s);
                """, {
                    'user_email': user_email,
                    'user_otp': otp,
                    'user_trips': False
                })


@click.command('test-create-user')
@with_appcontext
def test_create_user(user_email):
    pass
