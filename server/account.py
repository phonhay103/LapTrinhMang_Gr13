import sqlite3 as sql
import bcrypt
import pickle

from config import *

def _check_login(data):
    id, pw = pickle.loads(data)

    try:
        con = sql.connect(DATABASE)
        cur = con.cursor()
        query = f"SELECT password FROM user WHERE id = {id}"
        cur.execute(query)
        pw_hashed = cur.fetchone()
        con.close()

        if pw_hashed:
            pw_hashed = pw_hashed[0]
            return bcrypt.checkpw(pw.encode(), pw_hashed.encode())
        else:
            return False
    except sql.Error as er:
        return False             

def get_login_status(data):
    if _check_login(data):
        return pickle.dumps([200, 'Success'])
    else:
        return pickle.dumps([500, 'Error'])

def _get_hash_str(pw):
    pw = str(pw).encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw, salt)
    return hashed.decode()

def _check_change_password(data):
    id, new_pw = pickle.loads(data)
    new_pw = _get_hash_str(new_pw)
    
    try:
        con = sql.connect(DATABASE)
        cur = con.cursor()
        query = f"UPDATE user SET password = '{new_pw}' WHERE id = {id}"
        cur.execute(query)
        con.commit()
        con.close()
    except sql.Error as er:
        return False

    return True

def get_change_password_status(data):
    if _check_change_password(data):
        return pickle.dumps([200, 'Success'])
    else:
        return pickle.dumps([500, 'Error'])