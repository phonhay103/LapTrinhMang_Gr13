import pickle

def get_login_data(id, pw): # Send
    return pickle.dumps([100, id, pw])

def get_login_status(status): # Recv
    status = pickle.loads(status)
    if status[0] == 200:
        return True
    else:
        return False

def get_change_password_data(id, new_pw_1, new_pw_2): # Send
    if new_pw_1 == new_pw_2 and len(new_pw_1) > 0:
        return pickle.dumps([101, id, new_pw_1])
    else:
        return None

def get_change_password_status(status): # Recv
    status = pickle.loads(status)
    if status[0] == 200:
        return True
    else:
        return False

def get_logout_data(id): # Send
    return pickle.dumps([102, id])

def get_logout_status(status): # Recv
    status = pickle.loads(status)
    if status[0] == 200:
        return True
    else:
        return False