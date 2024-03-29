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

    def append(self, message):
        return Result(self.status,
                      self.message + message)


RESULT_DB_ERR = Result(False, 'A database error occurred')
