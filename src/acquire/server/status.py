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
    JOB_DOES_NOT_EXIST = 1003
    # User error codes
    NOT_LOGGED_IN = 2000
    # AWS Error Codes
    AWS_AUTHENTICATION_FAILED = 3000
    S3_URL_GENERATION_FAILED = 3001
    # Acquisition Error Codes
    FAILURE_VALIDATING_JOB = 4000
    FAILURE_ALLOCATING_JOB = 4001
    FAILURE_PROCESSING_JOB = 4002
