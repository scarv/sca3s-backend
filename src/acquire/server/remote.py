import requests, os, jwt, time
from acquire.server.status import JSONStatus
from acquire import share as share


class Remote():
    """
    Class for receiving jobs from SCARV API.
    """
    _access_token = None


    def _token_expired(self):
        """
        Calculates whether a token has expired.
        :return: Boolean representing whether a token has expired.
        """
        token = jwt.decode(self._access_token, verify=False)
        if (token["exp"]-5) <= time.time():
            return True
        else:
            return False


    def _authorize(self):
        """
        Used to authorize this program to commuinicate with SCARV API.
        """
        if (self._access_token is None) or (self._token_expired()):
            for i in range(3):
                res = requests.post("https://scarv.eu.auth0.com/oauth/token",
                                    headers={"Content-Type": "application/json"},
                                    json={
                                        "client_id": "BTYyO2udN3iKP3PY2Gcv2T1dMwzwO6kd",
                                        "client_secret": share.sys.conf.get( 'creds' ).get( 'client-secret', section = 'auth0' ),
                                        "audience": "https://lab.scarv.org",
                                        "grant_type": "client_credentials"
                                    })
                if res.status_code == 200:
                    credentials = res.json()
                    self._access_token = credentials["access_token"]
                    return
                else:
                    share.sys.log.info("[Auth0] Auth failure - trying again...")
                    share.sys.log.info(res.text)
                    time.sleep(1)
            share.sys.log.info("[Auth0] Authorization not successful")
            raise Exception("Auth0 Authorization failed.")


    def receive_job(self,devices):
        """
        Retrieves pending jobs from the SCARV API.
        """
        self._authorize()
        params = { 'device-db' : devices }
        headers = {"Authorization": "Bearer " + self._access_token}
        for i in range(3):
            res = requests.get("https://lab.scarv.org/api/job",
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
        self._authorize()
        remark = "archiving"
        if ( ( error_code is not None ) and ( error_code is not JSONStatus.SUCCESS ) ) :
            remark = "failed:" + str(error_code)
        headers = {"Authorization": "Bearer " + self._access_token}
        for i in range(3):
            res = requests.patch("https://lab.scarv.org/api/job/" + job_id,
                                 headers = headers,
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
