import socket
import threading
import pickle

from account import *
from config import *
from search import *

ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ThreadCount = 0
tree = create_tree()
user_id = None

try:
    ServerSideSocket.bind((HOST, PORT))
except socket.error as e:
    print(str(e))

print('Socket is listening..')
ServerSideSocket.listen(5)
conn, add = ServerSideSocket.accept()

while True:
    try: 
        data = pickle.loads(conn.recv(1024))
        if data[0] == 100:
            user_id, status = get_login_status(data[1], data[2])
        elif data[0] == 101:
            status = get_change_password_status(user_id, data[1], data[2])
        elif data[0] == 102:
            status = get_logout_status(user_id, data[1])
        elif data[0] == 103:
            status = search_for_index(tree, data[1])
        elif data[0] == 104:
            pass
        else:
            status = pickle.dumps([500, 'Error'])

        ServerSideSocket.send(status)
    except:
        conn.close()
        break
