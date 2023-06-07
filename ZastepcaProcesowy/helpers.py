from flask import redirect, session
from functools import wraps
import ast
import locale


def pln(value):
    locale.setlocale(locale.LC_ALL, "pl_PL.UTF-8")
    """Format value as PLN."""
    return (locale.currency(value, grouping=True))


def parse_tuple(string):
    try:
        s = ast.literal_eval(str(string))
        if type(s) == tuple:
            return s
        return
    except:
        return
        

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function