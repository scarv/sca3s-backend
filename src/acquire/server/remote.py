import requests, os, jwt, time
from acquire.server.status import JSONStatus


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
                                        "client_secret": os.environ["AUTH0_CLIENT_SECRET"],
                                        "audience": "https://lab.scarv.org",
                                        "grant_type": "client_credentials"
                                    })
                if res.status_code == 200:
                    credentials = res.json()
                    self._access_token = credentials["access_token"]
                    return
                else:
                    print ("[Auth0] Auth failure - trying again...")
                    print (res.text)
                    time.sleep(1)
            print ("[Auth0] Authorization not successful")
            raise Exception("Auth0 Authorization failed.")


    def receive_job(self):
        """
        Retrieves pending jobs from the SCARV API.
        :return: revocation list from UH Net API.
        """
        self._authorize()
        headers = {"Authorization": "Bearer " + self._access_token}
        for i in range(3):
            res = requests.get("https://lab.scarv.org/api/job",
                               headers = headers)
            if res.status_code == 200:
                job = res.json()
                if job["status"] == JSONStatus.SUCCESS:
                    return job
                else:
                    return None
            else:
                print ("[SCARV] API Communication Error - trying again...")
                print (res.text)
                time.sleep(1)
        print ("[SCARV] Error in API Communication")
        raise Exception("SCARV API Communication Error.")
