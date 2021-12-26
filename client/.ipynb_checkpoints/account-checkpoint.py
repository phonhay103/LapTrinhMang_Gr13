import pickle

def login():
    id = input('Mã số sinh viên: ')
    pw = input('Mật khẩu: ')
    return id, pickle.dumps([id, pw]) # Client save id

def get_login_status(status):
    status = pickle.loads(status)
    if status[0] == 200:
        print('Đăng nhập thành công')
        return True
    else:
        print('Error: Sai mã số sinh viên hoặc mật khẩu')
        return False

def change_password(id):
    new_pw_1 = input('Mật khẩu mới: ')
    new_pw_2 = input('Xác nhận mật khẩu: ')
    if new_pw_1 == new_pw_2:
        return pickle.dumps([id, new_pw_1])
    else:
        print('Error: Mật khẩu phải giống nhau!')
        return None

def get_change_password_status(status):
    status = pickle.loads(status)
    if status[0] == 200:
        print('Đổi mật khẩu thành công')
        return True
    else:
        print('Error: Lỗi không xác định')
        return False
