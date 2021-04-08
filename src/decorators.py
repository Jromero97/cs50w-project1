from flask import redirect, session
from functools import wraps


def sign_in_required(f):
    """
    Routes that requires an user signed in
    :param f: (email: string, password: string)
    :return: void
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/signin')
        return f(*args, **kwargs)
    return decorated_function
