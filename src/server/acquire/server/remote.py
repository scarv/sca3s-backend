import requests, os, time
from acquire.server.status import JSONStatus
from acquire import share as share


class Remote():
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
                share.sys.log.info("[SCARV] API Communication Error - trying again...")
                share.sys.log.info(res.text)
                time.sleep(1)
        share.sys.log.info("[SCARV] Error in API Communication")
        raise Exception("SCARV API Communication Error.")


    def complete_job(self, job_id, error_code=None):
        """
        Marks a job as finished on the SCARV API.
        :param job_id: Job ID to finish.
        :param error_code: If an error has occured, specify it here (JSONStatus enum only).
        """
        remark = "archiving"
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
                share.sys.log.info("[SCARV] Error in API Communication - " + info["status"])
                return
            else:
                share.sys.log.info("[SCARV] API Communication Error - trying again...")
                share.sys.log.info(res.text)
                time.sleep(1)
        share.sys.log.info("[SCARV] Error in API Communication")
        raise Exception("SCARV API Communication Error.")
