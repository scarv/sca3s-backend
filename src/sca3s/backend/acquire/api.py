# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import spec    as spec

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import enum, os, requests, time

class JSONStatus( enum.IntEnum ):
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

class APIImp( be.share.api.APIAbs ):
    """
    Class for receiving jobs from SCARV API.
    """
    _infrastructure_token = os.environ['INFRASTRUCTURE_TOKEN']


    def receive_job(self,devices):
        """
        Retrieves pending jobs from the SCARV API.
        """
        params = { 'device-db' : devices }
        headers = {"Authorization": "infrastructure " + self._infrastructure_token}
        for i in range(3):
            res = requests.get("https://lab.scarv.org/api/acquisition/job",
                               params = params,
                               headers = headers)
            if res.status_code == 200:
                job = res.json()
                if job["status"] == JSONStatus.SUCCESS:
                    return job
                else:
                    return None
            else:
                be.share.sys.log.info("[SCARV] API Communication Error - trying again...")
                be.share.sys.log.info(res.text)
                time.sleep(1)
        be.share.sys.log.info("[SCARV] Error in API Communication")
        raise Exception("SCARV API Communication Error.")


    def complete_job(self, job_id, error_code=None):
        """
        Marks a job as finished on the SCARV API.
        :param job_id: Job ID to finish.
        :param error_code: If an error has occured, specify it here (JSONStatus enum only).
        """
        remark = "complete"
        if ( ( error_code is not None ) and ( error_code is not JSONStatus.SUCCESS ) ) :
            remark = "failed:" + str(error_code)
        headers = {"Authorization": "infrastructure " + self._infrastructure_token}
        for i in range(3):
            res = requests.patch("https://lab.scarv.org/api/acquisition/job/" + job_id,
                                 headers=headers,
                                 json={
                                     "remark" : remark
                                 })
            if res.status_code == 200:
                info = res.json()
                if info["status"] == JSONStatus.SUCCESS:
                    return
                be.share.sys.log.info("[SCARV] Error in API Communication - " + info["status"])
                return
            else:
                be.share.sys.log.info("[SCARV] API Communication Error - trying again...")
                be.share.sys.log.info(res.text)
                time.sleep(1)
        be.share.sys.log.info("[SCARV] Error in API Communication")
        raise Exception("SCARV API Communication Error.")
