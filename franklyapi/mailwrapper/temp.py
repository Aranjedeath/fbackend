import boto.ses
conn = boto.ses.connect_to_region(
    'us-east-1',
    aws_access_key_id='AKIAJQQLEO5Q4TXXD2ZQ',
    aws_secret_access_key='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')


def add_email_sender(mail_id):
    return conn.verify_email_address(mail_id)


def get_verified_emails():
    return conn.list_verified_email_addresses()['ListVerifiedEmailAddressesResponse']['ListVerifiedEmailAddressesResult']['VerifiedEmailAddresses']
# print add_email_sender('nikhil@frankly.me')


def send_mail(sender_id, reciever_id, message_subject, message_body):
    conn.send_email(
        sender_id,
        message_subject,
        reciever_id,
        [reciever_id],
        format='html',
        bcc_addresses='nikhil@frankly.me')


@app.route('/endpoint', methods=['GET', 'POST'])
def hello_world():
    assert 0
    return 'Hello World!'

if __name__ == '__main__':
    # add_email_sender('nikhil@frankly.me')
    # for elem in get_verified_emails():
    # 	print elem
    send_mail()
    app.run()
