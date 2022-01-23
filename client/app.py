import socket
import streamlit as st
import cv2
import time
import pyautogui
import pickle

from config import *
from account import *

st.set_page_config(page_title='STSV', page_icon=':penguin:', layout="wide", initial_sidebar_state="auto", menu_items=None)

if 'socket' not in st.session_state:
    st.session_state.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP
    # st.session_state.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # IPv6, TCP
    ClientSocket = st.session_state.socket
    try:
        ClientSocket.connect((HOST, PORT))
    except socket.error as e:
        st.exception(e)
else:
    ClientSocket = st.session_state.socket

def app():
    # Template Page
    title = st.empty()
    bg = st.empty()
    searchContainer = st.empty()
    ChatContainer = st.empty()
    accountManagerContainer = st.empty()

    # Template Sidebar
    sidebar_title = st.sidebar.empty()
    user_id = st.sidebar.empty()
    loginForm = st.sidebar.empty()
    menuSelection = st.sidebar.empty()
    changePasswordForm = st.sidebar.empty()
    adminChatListContainer = st.sidebar.empty()

    # Init
    title.title("Sổ tay sinh viên")
    st.session_state.bg = True
    menus = ['Trang chủ', 'Đổi mật khẩu', 'Tra cứu', 'Tư vấn trực tuyến', 'Đăng xuất']
    guest_menus = ['Trang chủ','Tra cứu', 'Đăng xuất']
    admin_menus = ['Trang chủ', 'Đổi mật khẩu', 'Tư vấn trực tuyến', 'Đăng xuất']
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'index' not in st.session_state:
        st.session_state.index = DIR
    if 'show_all' not in st.session_state:
        st.session_state.show_all = False
    if 'r_id' not in st.session_state:
        st.session_state.r_id = None
    if 'history' not in st.session_state:
        st.session_state.history = None
    # ================================= Log in ============================== #
    if not st.session_state.logged_in:
        bg.image(cv2.imread('bg.png'), channels='BGR')
        with loginForm.form('Login'):
            id = st.text_input('Mã số sinh viên', max_chars=MSSV_CHARS, placeholder='VD: 20184172')
            pw = st.text_input('Mật khẩu', max_chars=PW_CHARS, type='password')
            loginBtn = st.form_submit_button('Đăng nhập')
            resetBtn = st.form_submit_button('Quên mật khẩu?') # Just for fun
            guestBtn = st.form_submit_button('Đăng nhập với tư cách khách')

            if resetBtn:
                st.info('Coming soon :smile:')

            if guestBtn:
                id = GUEST_ID
                pw = GUEST_PW
                loginBtn = True

            if loginBtn:
                if id and pw:
                    if id == 'admin':
                        id = ADMIN

                    if len(id) != MSSV_CHARS: # Check length
                        st.warning(f'Mã số sinh viên {id} phải có {MSSV_CHARS} ký tự!')
                    else: # Send to server
                        data = get_login_data(id, pw)
                        try:
                            ClientSocket.send(data)
                            status = ClientSocket.recv(1024)
                        except:
                            status = pickle.dumps([500, 'Error'])
        
                        if get_login_status(status):
                            st.session_state.logged_in = True
                            st.session_state.id = id
                            st.success(f'Đăng nhập thành công')
                            time.sleep(1)
                            
                            # Clear login form
                            loginForm.empty()
                        else:
                            st.error('Sai mã số sinh viên hoặc mật khẩu!')
                else:
                    st.warning('Hãy nhập mã số sinh viên hoặc mật khẩu!')
    # ================================= Log in ============================== #


    if st.session_state.logged_in:
        # ============================== Guest Menus ============================ #
        if st.session_state.id == GUEST_ID:
            st.session_state.option = menuSelection.selectbox('Menu', guest_menus)

            if st.session_state.option == guest_menus[0]:
                bg.image(cv2.imread('bg.png'), channels='BGR')

            # ============================= Search ============================= #
            elif st.session_state.option == guest_menus[1]:
                bg.empty()

                try:
                    ClientSocket.send(pickle.dumps([103, st.session_state.index]))
                    data_recv = b''
                    while True:
                        data_recv += ClientSocket.recv(1024)
                        try:
                            data = pickle.loads(data_recv)
                            break
                        except:
                            continue
                except Exception as e:
                    st.exception(e)

                with searchContainer.container():
                    if data[0] != 110:
                        st.write(data[0])
                        st.error('Error')
                        time.sleep(2)
                        searchContainer.empty()
                        st.session_state.index = DIR
                    else:
                        _, contents, indexes = data

                        st.markdown('\n'.join(contents), unsafe_allow_html=True)

                        if indexes[0][1] == 'parent':
                            t = "Xem thêm"
                            st.text('')
                            if st.button('Trở lại'):
                                st.session_state.index = indexes[0][0]
                                st.experimental_rerun()
                        else:
                            t = "Những điều sinh viên cần biết"

                        if len(indexes) > 1:
                            with st.expander(t, expanded=True):
                                indexes = indexes[1:]
                                buttons = []
                                for i, index, in enumerate(indexes):
                                    col1, col2 = st.columns((5, 1))
                                    col1.write(str(i+1) + '. ' + index[1])
                                    col1.write('')
                                    buttons.append((col2.button('Chi tiết', key=index[0]), index[0]))
                                    col2.write('')
                                
                                for button, index in buttons:
                                    if button:
                                        st.session_state.index = index
                                        st.experimental_rerun()
            # ============================= Search ============================= #


             # ============================= Log out ============================ #
            elif st.session_state.option == guest_menus[2]:
                data = get_logout_data(st.session_state.id)
                try:
                    ClientSocket.send(data)
                    status = ClientSocket.recv(1024)
                except:
                    status = pickle.dumps([500, 'Error'])

                if get_logout_status(status):
                    st.session_state.logged_in = False
                    del st.session_state['id']
                    st.sidebar.success('Đăng xuất thành công')
                    time.sleep(2)
                    pyautogui.press('f5')
                else:
                    st.sidebar.error('Đăng xuất không thành công!')
            # ============================= Log out ============================ #
        # ============================== Guest Menus ============================ #


        # ============================== Admin Menus ============================ #
        elif st.session_state.id == ADMIN:
            st.session_state.option = menuSelection.selectbox('Menu', admin_menus)

            if st.session_state.option == admin_menus[0]:
                bg.image(cv2.imread('bg.png'), channels='BGR')

            # ========================= Change password ========================= #
            elif st.session_state.option == admin_menus[1]:
                bg.image(cv2.imread('bg.png'), channels='BGR')

                with changePasswordForm.form('change_password'):
                    new_pw_1 = st.text_input('Mật khẩu mới:', max_chars=PW_CHARS, type='password')
                    new_pw_2 = st.text_input('Xác nhận mật khẩu mới:', max_chars=PW_CHARS, type='password')
                    changeBtn = st.form_submit_button('Đổi mật khẩu')

                    if changeBtn:
                        data = get_change_password_data(st.session_state.id, new_pw_1, new_pw_2)
                        if data:  # Send to server 
                            try:
                                ClientSocket.send(data)
                                status = ClientSocket.recv(1024)
                            except:
                                status = pickle.dumps([500, 'Error'])

                            if get_change_password_status(status):
                                st.success('Đổi mật khẩu thành công')
                                time.sleep(1)
                                
                                # Clear change password form
                                changePasswordForm.empty()
                                st.session_state.option = admin_menus[0]
                            else:
                                st.error('Đổi mật khẩu không thành công!')
                        else:
                            st.warning('Mật khẩu không hợp lệ!')
            # ========================= Change password ========================= #

            # ============================== Chat ============================== #
            elif st.session_state.option == admin_menus[2]:
                bg.empty()

                # Show chat list
                try:
                    ClientSocket.send(pickle.dumps([105, None, 'xXlistXx']))
                    status = ClientSocket.recv(1024)
                    status = pickle.loads(status)
                except Exception as e:
                    st.exception(e)
                    status = [500, 'Error']

                with adminChatListContainer.container():
                    if status[0] == 110:
                        buttons = [(st.button(lbl), lbl) for lbl in status[1]]
                    else:
                        st.error("Tính năng không khả dụng...")

                # Chat history
                for button, id in buttons:
                    if button:
                        st.session_state.r_id = id
                        break
                if st.session_state.r_id:
                    try:
                        ClientSocket.send(pickle.dumps([105, st.session_state.r_id, 'xXloadXx']))
                        data_recv = b''
                        while True:
                            data_recv += ClientSocket.recv(1024)
                            try:
                                data = pickle.loads(data_recv)
                                break
                            except:
                                continue
                    except Exception as e:
                        st.exception(e)
                        data = [500, 'Error']

                    # Chat GUI
                    if data[0] == 110:
                        with ChatContainer.form('chat_form'):
                            if st.session_state.show_all:
                                messages = data[1]
                            else:
                                if len(data[1]) > 5:
                                    messages = data[1][-5:]
                                else:
                                    messages = data[1]

                            for msg_id, _, msg_data, t in messages:
                                msg_id = str(msg_id)
                                if msg_id == ADMIN:
                                    st.write(f'_**Admin**_ ({t}): {msg_data}')
                                else:
                                    st.write(f'_**{msg_id}**_ ({t}): {msg_data}')
                            st.write('')

                            msg = st.text_input('Nhập tin nhắn', placeholder='Aa')
                            btnSend = st.form_submit_button('Gửi')
                            btnShowAll = st.form_submit_button('Xem lịch sử')
                            btnRemove = st.form_submit_button('Xóa tin nhắn')

                            if btnSend:
                                st.session_state.show_all = False
                                try:
                                    ClientSocket.send(pickle.dumps([105, st.session_state.r_id, msg]))
                                    status = ClientSocket.recv(1024)
                                    status = pickle.loads(status)[0]
                                except:
                                    st.exception(e)
                                    status = 500

                                if status == 200:
                                    st.experimental_rerun()
                                else:
                                    st.warning('Message không khả dụng!')

                            if btnShowAll:
                                st.session_state.show_all = True
                                st.experimental_rerun()

                            if btnRemove:
                                st.session_state.show_all = False
                                try:
                                    ClientSocket.send(pickle.dumps([105, st.session_state.r_id, 'xXremoveXx']))
                                    status = ClientSocket.recv(1024)
                                    status = pickle.loads(status)[0]
                                except:
                                    st.exception(e)
                                    status = 500

                                if status == 200:
                                    st.session_state.r_id = None
                                    st.success('Xóa tin nhắn thành công')
                                    time.sleep(1)
                                    st.experimental_rerun()
                                else:
                                    st.write('abc')
                                    st.warning('Tính năng không khả dụng...')
                    else:
                        ChatContainer.write('xyz')
                        ChatContainer.error("Tính năng không khả dụng....")
            # ============================== Chat ============================== #


            # ============================= Log out ============================ #
            elif st.session_state.option == admin_menus[3]:
                data = get_logout_data(st.session_state.id)
                try:
                    ClientSocket.send(data)
                    status = ClientSocket.recv(1024)
                except:
                    status = pickle.dumps([500, 'Error'])

                if get_logout_status(status):
                    st.session_state.logged_in = False
                    del st.session_state['id']
                    st.sidebar.success('Đăng xuất thành công')
                    time.sleep(2)
                    pyautogui.press('f5')
                else:
                    st.sidebar.error('Đăng xuất không thành công!')
            # ============================= Log out ============================ #
        # ============================== Admin Menus ============================ #


        # ============================== User Menus ============================= #
        else:
            st.session_state.option = menuSelection.selectbox('Menu', menus)

            if st.session_state.option == menus[0]:
                bg.image(cv2.imread('bg.png'), channels='BGR')

            # ========================= Change password ========================= #
            elif st.session_state.option == menus[1]:
                bg.image(cv2.imread('bg.png'), channels='BGR')

                with changePasswordForm.form('change_password'):
                    new_pw_1 = st.text_input('Mật khẩu mới:', max_chars=PW_CHARS, type='password')
                    new_pw_2 = st.text_input('Xác nhận mật khẩu mới:', max_chars=PW_CHARS, type='password')
                    changeBtn = st.form_submit_button('Đổi mật khẩu')

                    if changeBtn:
                        data = get_change_password_data(st.session_state.id, new_pw_1, new_pw_2)
                        if data:  # Send to server 
                            try:
                                ClientSocket.send(data)
                                status = ClientSocket.recv(1024)
                            except:
                                status = pickle.dumps([500, 'Error'])

                            if get_change_password_status(status):
                                st.success('Đổi mật khẩu thành công')
                                time.sleep(1)
                                
                                # Clear change password form
                                changePasswordForm.empty()
                                st.session_state.option = menus[0]
                            else:
                                st.error('Đổi mật khẩu không thành công!')
                        else:
                            st.warning('Mật khẩu không hợp lệ!')
            # ========================= Change password ======================== #


            # ============================= Search ============================= #
            elif st.session_state.option == menus[2]:
                bg.empty()

                try:
                    ClientSocket.send(pickle.dumps([103, st.session_state.index]))
                    data_recv = b''
                    while True:
                        data_recv += ClientSocket.recv(1024)
                        try:
                            data = pickle.loads(data_recv)
                            break
                        except:
                            continue
                except Exception as e:
                    st.exception(e)

                with searchContainer.container():
                    if data[0] != 110:
                        st.write(data[0])
                        st.error('Error')
                        time.sleep(2)
                        searchContainer.empty()
                        st.session_state.index = DIR
                    else:
                        _, contents, indexes = data

                        st.markdown('\n'.join(contents), unsafe_allow_html=True)
                        if len(contents) > 0:
                            st.session_state.history = contents[0].rstrip()
                        else:
                            st.session_state.history = st.session_state.index
                            
                        if indexes[0][1] == 'parent':
                            t = "Xem thêm"
                            st.text('')
                            if st.button('Trở lại'):
                                st.session_state.index = indexes[0][0]
                                st.experimental_rerun()
                        else:
                            t = "Những điều sinh viên cần biết"

                        if len(indexes) > 1:
                            with st.expander(t, expanded=True):
                                indexes = indexes[1:]
                                buttons = []
                                for i, index, in enumerate(indexes):
                                    col1, col2 = st.columns((5, 1))
                                    col1.write(str(i+1) + '. ' + index[1])
                                    col1.write('')
                                    buttons.append((col2.button('Chi tiết', key=index[0]), index[0]))
                                    col2.write('')
                                
                                for button, index in buttons:
                                    if button:
                                        st.session_state.index = index
                                        st.experimental_rerun()
            # ============================= Search ============================= #


            # ============================== Chat ============================== #
            elif st.session_state.option == menus[3]:
                bg.empty()
                # Chat history
                try:
                    ClientSocket.send(pickle.dumps([104, 'xXloadXx']))
                    data_recv = b''
                    while True:
                        data_recv += ClientSocket.recv(1024)
                        try:
                            data = pickle.loads(data_recv)
                            break
                        except:
                            continue
                except Exception as e:
                    st.exception(e)
                    data = [500, 'Unknown']

                # Send topic
                if st.session_state.history is not None and st.session_state.history != DIR:
                    try:
                        ClientSocket.send(pickle.dumps([104, st.session_state.history]))
                        ClientSocket.recv(1024)
                    except:
                        st.exception(e)
                    st.session_state.history = None
                    st.experimental_rerun()

                # Chat GUI
                if data[0] == 110:
                    with ChatContainer.form('chat_form'):
                        if st.session_state.show_all:
                            messages = data[1]
                        else:
                            if len(data[1]) > 5:
                                messages = data[1][-5:]
                            else:
                                messages = data[1]

                        for msg_id, _, msg_data, t in messages:
                            msg_id = str(msg_id)
                            if msg_id == ADMIN:
                                st.write(f'_**Admin**_ ({t}): {msg_data}')
                            else:
                                st.write(f'_**{msg_id}**_ ({t}): {msg_data}')
                            st.write('')

                        msg = st.text_input('Nhập tin nhắn', placeholder='Aa')
                        btnSend = st.form_submit_button('Gửi')
                        btnShowAll = st.form_submit_button('Xem lịch sử')

                        if btnSend:
                            st.session_state.show_all = False
                            try:
                                ClientSocket.send(pickle.dumps([104, msg]))
                                status = ClientSocket.recv(1024)
                                status = pickle.loads(status)[0]
                            except:
                                st.exception(e)
                                status = 500

                            if status == 200:
                                st.experimental_rerun()
                            else:
                                st.warning('Message không khả dụng..')

                        if btnShowAll:
                            st.session_state.show_all = True
                            st.experimental_rerun()
                else:
                    ChatContainer.error("Tính năng không khả dụng.")
            # ============================== Chat ============================== #


            # ============================= Log out ============================ #
            elif st.session_state.option == menus[4]:
                data = get_logout_data(st.session_state.id)
                try:
                    ClientSocket.send(data)
                    status = ClientSocket.recv(1024)
                except:
                    status = pickle.dumps([500, 'Error'])

                if get_logout_status(status):
                    st.session_state.logged_in = False
                    del st.session_state['id']
                    st.sidebar.success('Đăng xuất thành công')
                    time.sleep(2)
                    pyautogui.press('f5')
                else:
                    st.sidebar.error('Đăng xuất không thành công!')
            # ============================= Log out ============================ #
        # ============================= User Menus ============================= #
try:
    app()
except socket.error as e:
    st.exception(e)
    ClientSocket.close()