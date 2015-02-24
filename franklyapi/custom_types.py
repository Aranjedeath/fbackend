import models

def username(value):
    try:
        models.User.query.filter(models.User.username==value).one()
        return value
    except:
        raise Exception('User does not exists.')

def admin_user(value):
    try:
        models.AdminUser.query.filter(models.AdminUser.user_id==value).one()
        return value
    except:
        raise Exception('User is not an admin.')