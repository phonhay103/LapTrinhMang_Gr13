import pickle
import os
import sqlite3 as sql
import datetime

from config import *

def chat_save(s_id, r_id, msg):
    try:
        con = sql.connect(CHAT_DB)
        cur = con.cursor()
        query = f"INSERT INTO chat(send_id, recv_id, msg, time) VALUES('{s_id}', '{r_id}', '{msg}', \'{datetime.datetime.today().strftime('%d/%m/%Y %H:%M:%S')}\')"
        cur.execute(query)
        con.commit()
        con.close()
    except sql.Error as er:
        return pickle.dumps([500, 'Error'])
    else:    
        return pickle.dumps([200, 'Success'])

def chat_load(id):
    try:
        con = sql.connect(CHAT_DB)
        cur = con.cursor()
        query = f"SELECT * FROM chat WHERE send_id = '{id}' OR recv_id = '{id}'"
        cur.execute(query)
        result = cur.fetchall()
        con.close()
    except sql.Error as er:
        return pickle.dumps([500, 'Error'])
    else:        
        return pickle.dumps([110, result])

def chat_list():
    try:
        con = sql.connect(CHAT_DB)
        cur = con.cursor()
        query = f"SELECT DISTINCT(send_id) FROM chat WHERE send_id != '{ADMIN_ID}' ORDER BY time DESC"
        cur.execute(query)
        result = [str(i[0]) for i in cur.fetchall()]
        con.close()
    except sql.Error as er:
        return pickle.dumps([110, []])
    else:
        return pickle.dumps([110, result])

def chat_remove(id):
    try:
        con = sql.connect(CHAT_DB)
        cur = con.cursor()
        query = f"DELETE FROM chat WHERE send_id = '{id}' OR recv_id = '{id}'"
        cur.execute(query)
        con.commit()
        con.close()
    except sql.Error as er:
        return pickle.dumps([500, 'Error'])
    else:
        return pickle.dumps([200, 'Success'])