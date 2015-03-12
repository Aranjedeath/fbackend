import time
from configs import config
from apns import APNs, Frame, Payload



class APN():

    def __init__(self, cert_file=config.APN_CERT_PATH, key_file=config.APN_KEY_PATH, use_sandbox=False):
        self.apns = APNs(use_sandbox=use_sandbox, cert_file=cert_file, key_file=key_file)

    def send_message(self, push_ids, data):
    	payload = Payload(custom=data)
    	expiry = time.time()+3600*12
    	priority = 10
    	identifier = data['id']

    	frame = Frame()

    	for push_id in push_ids:
    		frame.add_item(push_id, payload, identifier, expiry, priority)
		self.apns.gateway_server.send_notification_multiple(frame)
		