#!/usr/bin/python3

import sys
import getopt
from reponsehandler import Handler

def main(argv):

    # consider adding -n (--name) firename
    # to get basic info about the fire with that name

    # consider adding -n (--name) firename
    # to get basic info about the fire with that name

    handler = Handler()

    try:
        opts, args = getopt.getopt(argv, "hd:x:y:", ["dist=", "lon=", "lat="])
    except getopt.GetoptError:
        print('test.py -d <dist> -x <lon> -y <lat>')
        sys.exit(2)

    handler.response(opts)


if __name__ == "__main__":
    main(sys.argv[1:])
