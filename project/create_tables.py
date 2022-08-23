import sqlite3
import configparser
from sql_queries import drop_table_queries
from sql_queries import create_table_queries


def main():

    config = configparser.ConfigParser()
    config.read_file(open('inReach.cfg'))

    con = sqlite3.connect(config.get('SQLITE', 'DBNAME'))
    cur = con.cursor()

    check = input("Really Drop Tables? Y/n")
    if check == "Y":

        print("______DROPPING TABLES______")
        for qry in drop_table_queries:
            cur.execute(qry)

        print("______CREATING TABLES______")
        for qry in create_table_queries:
            cur.execute(qry)

    con.commit()
    con.close()


if __name__ == "__main__":
    main()
