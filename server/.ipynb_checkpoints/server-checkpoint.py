import socket
import pickle
import selectors
import types

from account import *
from config import *
from search import *

tree = create_tree()
sel = selectors.DefaultSelector()
ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
                print('Receiving:', data.data)
            except:
                data.data = [500, "Error"]
        else:
            print('Closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()

    # Send
    if mask & selectors.EVENT_WRITE:
        if data.data:
            print('Parsing:', data.data, data.addr)
            try:
                if data.data[0] == 100:
                    print('Log in:', data.id, data.addr)
                    data.id, status = get_login_status(data.data[1], data.data[2])
                    print('Log in:', data.id, data.addr)
                elif data.data[0] == 101:
                    print('Change Password:', data.id, data.addr)
                    status = get_change_password_status(data.id, data.data[1], data.data[2])
                    print('Change Password:', data.id, data.addr)
                elif data.data[0] == 102:
                    print('Logout:', data.id, data.addr)
                    data.id, status = get_logout_status(data.id, data.data[1])
                    print('Logout:', data.id, data.addr)
                elif data.data[0] == 103:
                    print('Search:', data.id, data.addr)
                    status = search_for_index(tree, data.data[1])
                elif data.data[0] == 104:
                    print('NAN')
                    status = pickle.dumps([500, 'Error'])
                else:
                    print('Error?')
                    status = pickle.dumps([500, 'Error'])
            except Exception as e:
                print(e)
                status = pickle.dumps([500, 'Error'])
            data.data = None
            
            try:
                sock.sendall(status)
                print('Sent to', data.addr)
            except socket.error as e:
                print('Cannot sent data to', data.addr)

try:
    ServerSideSocket.bind((HOST, PORT))
except socket.error as e:
    print(str(e))
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