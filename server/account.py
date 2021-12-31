import sqlite3 as sql
import bcrypt
import pickle

from config import *

def _check_login(id, pw): # Recv
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

def get_login_status(id, pw): # Send
    try:
        if _check_login(id, pw):
            return id, pickle.dumps([200, 'Success'])
        else:
            return None, pickle.dumps([500, 'Error'])
    except:
        return None, pickle.dumps([500, 'Error'])

def _get_hash_str(pw):
    pw = str(pw).encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw, salt)
    return hashed.decode()

def _check_change_password(id, new_pw): # Recv
    try:
        new_pw = _get_hash_str(new_pw)
        
        con = sql.connect(DATABASE)
        cur = con.cursor()
        query = f"UPDATE user SET password = '{new_pw}' WHERE id = {id}"
        cur.execute(query)
        con.commit()
        con.close()
    except sql.Error as er:
        return False

    return True

def get_change_password_status(user_id, id, new_pw): # Send
    try:
        if user_id is None or user_id != id:
            return pickle.dumps([500, 'Error'])
        elif _check_change_password(id, new_pw):
            return pickle.dumps([200, 'Success'])
        else:
            return pickle.dumps([500, 'Error'])
    except:
        return pickle.dumps([500, 'Error'])

def get_logout_status(user_id, id):
    try:
        if user_id is None or user_id != id:
            return pickle.dumps([500, 'Error'])
        elif user_id == id:
            return pickle.dumps([200, 'Success'])
        else:
            return pickle.dumps([500, 'Error'])
    except:
        return pickle.dumps([500, 'Error'])