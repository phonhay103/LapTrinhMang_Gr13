import socket
import pickle
import selectors
import types

from account import *
from config import *
from search import *
from chat import *

tree = create_tree()
sel = selectors.DefaultSelector()
# ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP
ServerSideSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # IPv6, TCP

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print('Accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, data=None, id=None)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    # Recv
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)
        except:
            recv_data = None

        if recv_data:
            try:
                data.data = pickle.loads(recv_data)
                print('Receiving:', data.data, data.addr)
            except:
                data.data = [500, "Error"]
        else:
            print('Closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()

    # Send
    if mask & selectors.EVENT_WRITE:
        if data.data:
            try:
                if data.data[0] == 100:
                    print('Log in:', data.data[1])
                    data.id, status = get_login_status(data.data[1], data.data[2])
                elif data.data[0] == 101:
                    print('Change Password:', data.id)
                    status = get_change_password_status(data.id, data.data[1], data.data[2])
                elif data.data[0] == 102:
                    print('Logout:', data.id)
                    data.id, status = get_logout_status(data.id, data.data[1])
                elif data.data[0] == 103:
                    print('Search:', data.id, data.data[1])
                    status = search_for_index(tree, data.data[1])
                elif data.data[0] == 104:
                    print('Chat User:', data.id)
                    if data.data[1] == 'xXloadXx':
                        status = chat_load(data.id)
                    else:
                        status = chat_save(data.id, data.id, data.data[1])
                elif data.data[0] == 105:
                    print('Chat Admin:', data.id)
                    if data.data[2] == 'xXloadXx':
                        status = chat_load(data.data[1])
                    elif data.data[2] == 'xXlistXx':
                        status = chat_list()
                    elif data.data[2] == 'xXremoveXx':
                        status = chat_remove(data.data[1])
                    else:
                        status = chat_save(ADMIN_ID, data.data[1], data.data[2])
                else:
                    status = pickle.dumps([500, 'Error'])
            except Exception as e:
                print(e)
                status = pickle.dumps([500, 'Error'])
            data.data = None
            
            try:
                sock.sendall(status)
                print('Send:', data.addr, pickle.loads(status))
            except socket.error as e:
                print('Cannot sent data to', data.addr)

try:
    ServerSideSocket.bind((HOST, PORT))
except socket.error as e:
    print(e)
    exit()

print('Listening on', (HOST, PORT))
ServerSideSocket.listen()
ServerSideSocket.setblocking(False)
sel.register(ServerSideSocket, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)