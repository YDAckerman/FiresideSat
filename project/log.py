# from https://stackoverflow.com/questions/4722745/logging-between-classes-in-python

import logging
log = logging.getLogger('fireside_log')
log.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

# Log to file
filehandler = logging.FileHandler("fireside_log.txt", "w")
filehandler.setLevel(logging.DEBUG)
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

# Log to stdout too
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)
streamhandler.setFormatter(formatter)
log.addHandler(streamhandler)


def main():
    log.debug("THIS IS A TEST")
    log.error("THIS IS AN ERROR")
    try:
        will_fail()
    except:
        log.exception("THERE WAS AN EXCEPTION")

if __name__ == '__main__':
    main()
