import boto.ses
import json

from flask import Flask, url_for, request

app = Flask(__name__)



def add_email_sender(mail_id):
    return conn.verify_email_address(mail_id)


def get_verified_emails():
    return conn.list_verified_email_addresses()['ListVerifiedEmailAddressesResponse']['ListVerifiedEmailAddressesResult']['VerifiedEmailAddresses']
# print add_email_sender('nikhil@frankly.me')


@app.route('/endpoint', methods=['GET', 'POST'])
def hello_world():
    print request.headers
    data = json.loads(request.data)
    print "\n\n Data \n -------------\n",json.loads(data['Message'])['mail']['destination'][0]
    return 'Hello World!'

if __name__ == '__main__':
    # add_email_sender('nikhil@frankly.me')
    # for elem in get_verified_emails():
    # 	print elem
    # send_mail()
    app.run(debug=True, host='0.0.0.0', port=8888)
