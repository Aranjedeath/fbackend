from configs import config
import gcm

class GCM():

    def __init__(self, api_key=config.API_KEY):
        self.gcm = gcm.GCM(api_key)

    def send_message(self, registration_ids, data):
        self.gcm.json_request(registration_ids=registration_ids, data=data)
