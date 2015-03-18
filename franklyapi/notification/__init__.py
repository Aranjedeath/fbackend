#from config import consider_for_notification

from make_notification import *


def idreamofsapru(cur_user_id,question_id):
    from models import User,AccessToken
    from controllers import get_device_type
    from GCM_notification import GCM
    import datetime
    import CustomExceptions
    from sqlalchemy.orm.exc import NoResultFound

    try:
        user = User.query.filter(User.id == cur_user_id).one()
        gcm_sender = GCM()
        for device in AccessToken.query.filter(AccessToken.user==cur_user_id,
                                            AccessToken.active==True,
                                            AccessToken.push_id!=None).all():
            payload = { "user_to": user.id,
                        "type": 1,
                        "id": question_id,
                        "text": "To win Indian jersey, get maximum upvotes on your question to Jatin Sapru!",
                        "styled_text": "Hello!",
                        "icon": None,
                        "group_id": question_id,
                        "link": "http://frankly.me",
                        "deeplink": "http://frankly.me/q/%s" % question_id,
                        "timestamp": '123456798',
                        "seen": False,
                        "heading": "Frankly.me"
            }
            if get_device_type(device.device_id) == 'android':  
                gcm_sender.send_message([device.push_id], payload)

    except NoResultFound:
        raise CustomExceptions.UserNotFoundException('User Not Found')