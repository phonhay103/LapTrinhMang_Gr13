import socket
import pickle
import time

from config import *

# s = ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((HOST, PORT))

# def send(s, data):
#     data = pickle.dumps(data)
#     s.send(data)
#     msg = s.recv(1024)
#     return pickle.loads(msg)


# login_status = send(s, [100, '20184218', '20184218'])
# change_password_status = send(s, [101, '20184218', '20184218'])
# logout_status = send(s, [103, '32'])

# s.close()

while True:
    print('A', time.localtime)
    time.sleep(1)
    