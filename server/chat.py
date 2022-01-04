import pickle
import os

from config import *

def chat_save(s_id, r_id, msg):
    try:
        with open(f'{CHAT_DIR}/{r_id}.txt', 'a', encoding='utf8') as f:
            f.write(f'{s_id}@{msg}\n')
    except:
        return pickle.dumps([500, 'Error'])
        
    return pickle.dumps([200, 'Success'])

def chat_load(id):
    path = f'{CHAT_DIR}/{id}.txt'
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf8') as f:
            return pickle.dumps([110, f.readlines()])
    else:
        return pickle.dumps([110, []])

def chat_list():
    id_list = [id.split('.')[0] for id in os.listdir(CHAT_DIR)]
    return pickle.dumps([110, id_list])