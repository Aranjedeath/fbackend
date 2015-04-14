from models import AccessToken


def get_active_mobile_devices(user_id):

    devices = AccessToken.query.filter(AccessToken.user == user_id, AccessToken.active==True,
                             AccessToken.push_id != None).all()
    return devices