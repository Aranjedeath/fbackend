from configs import config
from apns import APNs, Frame, Payload
import random



class APN():

    def __init__(self, cert_file=config.APN_CERT_PATH, key_file=config.APN_KEY_PATH, use_sandbox=False):
        self.apns = APNs(use_sandbox=True, cert_file=cert_file, key_file=key_file, enhanced=True)



    def send_message(self, apn_ids, data):

        def response_listener(error_response):
            print error_response

        payload = Payload(custom=data)
        identifier = random.getrandbits(32)
        self.apns.gateway_server.register_response_listener(response_listener)

        for id in apn_ids:
            self.apns.gateway_server.send_notification(id, payload, identifier=identifier)

        # expiry = time.time()+3600*12
        # priority = 10
        # identifier = 1  #data['id']
        #
        # frame = Frame()
        #
        # for apn_id in apn_ids:
        #     frame.add_item(apn_id, payload, identifier, expiry, priority)
        # self.apns.gateway_server.send_notification_multiple(frame)
