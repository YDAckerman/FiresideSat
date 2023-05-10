import psycopg2
import configparser
import random
from helpers.comms import Comms
from flask import g

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


def add_new_user(cur, email, mapshare_id, mapshare_password):

    # check if user exists
    # (if so, direct to reset password;
    # must provide new mapshare pw, too)
    user_exists = cur.execute(
        """
        SELECT 1
        FROM users
        WHERE user_email = %(user_email)s AND
        mapshare_id = %(mapshare_id)s AND
        mapshare_pw = %(mapshare_pw)s;
        """)

    if user_exists:
        return '<h1>This user already exists.</h1>'

    device_coms = Comms()

    otp = ''.join([str(random.randint(OTP_LOWER,
                                      OTP_UPPER))
                   for _ in range(OTP_LEN)])

    # result = device_coms.send_user_message(mapshare_id,
    #                                        mapshare_password,
    #                                        otp)

    result = b'deviceIds=448739&messageText=testing+from+selenium&fromAddr=no.reply%40firesidesat.com'

    if result:
        try:
            # if user does not exist insert new user
            # and get new user id
            cur.execute(
                """UPDATE devices
                   SET garmin_device_id = %(device_id)s
                   WHERE device_id = (INSERT INTO devices (user_id)
                                      VALUES (INSERT INTO users
                                                     (user_email, user_pw,
                                                      mapshare_id,
                                                      mapshare_pw)
                                              VALUES (%(user_email)s,
                                                      %(otp)s,
                                                      %(mapshare_id)s,
                                                      %(mapshare_pw)s)
                                              RETURNING user_id)
                                      RETURNING device_id);""",
                {'user_email': email,
                 'user_otp': otp,
                 'mapshare_id': mapshare_id,
                 'mapshare_pw': mapshare_password,
                 'device_id': device_coms.extract_device_id(result)
                 })

            return '<h1>Registration Succesful.</h1>' \
                + '<h1>Please check your InReach' \
                + ' device for your temporary password.</h1>' \
                + '<h1>The message may take a while to arrive.</h1>'

        except Exception as e:
            print(e)
            return '<h1>Something went wrong with the database</h1>'
    else:
        return '<h1>Something went wrong when setting an OTP</h1>'
