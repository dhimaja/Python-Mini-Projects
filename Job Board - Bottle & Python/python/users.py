"""
Created on Mar 26, 2012

@author: steve
"""
from database import password_hash
import bottle
from bottle import request

# this variable MUST be used as the name for the cookie used by this application
COOKIE_NAME = 'sessionid'


def check_login(db, usernick, password):
    """returns True if password matches stored"""
    cursor = db.cursor()
    query = """SELECT password FROM users WHERE nick=?"""
    cursor.execute(query, [usernick])
    passcheck = cursor.fetchone()

    print(passcheck)
    print(password)
    if passcheck:
        plain=passcheck[0]
        encrypt = password_hash(password)
        if encrypt == plain:
            return True
        else:
            return False
    else:
        return False


def generate_session(db, usernick):
    """create a new session and add a cookie to the response object (bottle.response)
    user must be a valid user in the database, if not, return None
    There should only be one session per user at any time, if there
    is already a session active, use the existing sessionid in the cookie
    """
    set_result = user_present(db, usernick)
    if set_result:
        cursor = db.cursor()
        query_id = """SELECT sessionid FROM sessions WHERE usernick=?"""
        cursor.execute(query_id, [usernick])
        sid = cursor.fetchone()
    else:
        return None
    if sid is None:
           sessionid = put_session(db, usernick)

    else:
           sessionid = sid[0]

    bottle.response.set_cookie(COOKIE_NAME, sessionid)
    return sessionid





def delete_session(db, usernick):
    """remove all session table entries for this user"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM sessions where usernick=(?);", (usernick,))
    db.commit()

def user_present(db,usernick):
    """ if user exists returns true"""
    cursor = db.cursor()
    result = """SELECT avatar FROM users where nick=? """
    cursor.execute(result,[usernick])
    present = cursor.fetchone()
    if present:
        return True
    else:
        return False

def put_session(db, usernick):
    """if session dosent exist , inserts session and returns inserted sessionid"""
    cursor = db.cursor()
    put = """INSERT into sessions (sessionid, usernick) values(?,?)"""
    sessionid = usernick + "uses"
    cursor.execute(put, [sessionid, usernick])
    db.commit()
    return sessionid




def session_user(db):
    """try to  retrieve the user from the sessions table
    return usernick or None if no valid session is present"""
    sessionid = request.get_cookie(COOKIE_NAME)
    if sessionid is None:
     return None

    else:
         cursor = db.cursor()
         query = """SELECT usernick from sessions where sessionid=?"""
         cursor.execute(query, [sessionid])
         uses = cursor.fetchone()
         if uses is None:
             return None
         else:
             usernick = uses[0]

             return usernick

def get_avatar(db, usernick):
    """Returns the avatar of the logged in user"""
    sessionid = request.get_cookie(COOKIE_NAME)
    """Here we retrieve the sessionid from the cookie"""
    if sessionid:
        cursor = db.cursor()
        query = """SELECT avatar FROM users WHERE nick=?"""
        cursor.execute(query, [usernick])
        image = cursor.fetchone()
        if image:
            avatar = image[0]
            return avatar
        else:
            return None
    else:
        return None



