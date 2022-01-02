import socket
import pickle

from config import *

s = ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def send(s, data):
    data = pickle.dumps(data)
    s.send(data)
    msg = s.recv(1024)
    print(pickle.loads(msg))

# Test login
# send(s, [100, '1', '1'])
# send(s, [100, '20180000', '20180000'])
send(s, [100, '20184218', '20184218'])

# Test change password
# send(s, [101, '1', '1'])
# send(s, [101, '20184218', '20184218'])

# Test logout
# send(s, [102, '1'])
# send(s, [102, '32'])

# Test search
data = pickle.dumps([103, '1'])
s.send(data)
msg = b''
while True:
    recv = s.recv(1024)
    msg += recv
    try:
        data = pickle.loads(msg)
        break
    except:
        print(False)

print(data)
s.close()