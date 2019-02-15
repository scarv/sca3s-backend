from enum import IntEnum


class JSONStatus(IntEnum):
    """
    Class to define status codes for use with the OKException class.
    By default `status : 0` should be included with all API requests.
    """
    # Global Success Code
    SUCCESS = 0
    # Job error codes
    NO_ITEMS_ON_QUEUE = 1000
    INVALID_JOB_SYNTAX = 1001
    TOO_MANY_QUEUED_JOBS = 1002
    # User error codes
    NOT_LOGGED_IN = 2000
    # AWS Error Codes
    AWS_AUTHENTICATION_FAILED = 3000