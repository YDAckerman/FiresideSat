import sys


class Result():

    def __init__(self, status, message):
        self.status = status
        self.message = message

    def print_to_console(self):
        if self.status:
            print("Success: " + self.message, file=sys.stdout)
        else:
            print("Failure: " + self.message, file=sys.stderr)

    def append(self, res):
        self.status &= res.status
        self.message += res.message


RESULT_DB_ERR = Result(False, 'A database error occurred')
