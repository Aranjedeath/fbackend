from configs import config
import gcm

class GCM():

    def __init__(self, api_key=config.GCM_API_KEY):
        self.gcm = gcm.GCM(api_key)

    def send_message(self, gcm_ids, data):
        self.gcm.json_request(registration_ids=gcm_ids, data=data)
