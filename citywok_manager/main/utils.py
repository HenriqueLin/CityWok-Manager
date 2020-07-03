from flask_login import current_user


def get_pk(obj):
    return str(obj)


def get_current_user_id():
    if current_user:
        return current_user.id
    else:
        return None
