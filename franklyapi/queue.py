import boto.sqs
from boto.sqs.message import Message
import json
import csv
from configs import config

from app import raygun

def pickle_dict_to_message(dict_structure):
    json_string = json.dumps(dict_structure)
    m = Message()
    m.set_body(json_string)
    return m

AWS_KEY = config.AWS_KEY
AWS_SECRET = config.AWS_SECRET

class SQSQueue:
    def __init__(self, queue_name, message_visibility_timeout = 60):
        conn = boto.sqs.connect_to_region(
                "ap-southeast-1",
                aws_access_key_id=AWS_KEY,
                aws_secret_access_key=AWS_SECRET)
        self.q = conn.get_queue(queue_name)

        if not self.q:
            self.q = conn.create_queue(queue_name, message_visibility_timeout)
        # print self.q

    def push(self, data_dict):
        m = pickle_dict_to_message(data_dict)
        self.q.write(m)
        return 0

    def peek(self):
        m = self.q.read()
        if m:
            return json.loads(m.get_body())
        else:
            return None

    def pop(self):
        m = self.q.read()
        if m:
            m.delete()
            return json.loads(m.get_body())
        else:
            return None

    def process(self,func):
        m = self.q.read()
        if m:
            try:
                return_code = func(json.loads(m.get_body()))
                if return_code == 0:
                    m.delete()
                return return_code
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                raygun.send(exc_type, exc_value, exc_traceback)
                return -1
                print "Message retained in queue because of", e
        return 1

    def __str__(self):
        return str(self.q)


if __name__ == '__main__':
    sq = SQSQueue('test1')
    print sq.peek()