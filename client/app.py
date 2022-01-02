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
    st.session_state.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    # Template Sidebar
    sidebar_title = st.sidebar.empty()
    user_id = st.sidebar.empty()
    loginForm = st.sidebar.empty()
    menuSelection = st.sidebar.empty()
    changePasswordForm = st.sidebar.empty()
    adminChatListContainer = st.sidebar.empty()

    # Init
    title.title("Sổ tay sinh viên 2021")
    bg.image(cv2.imread('bg.png'), channels='BGR')
    st.session_state.bg = True
    menus = ['Trang chủ', 'Đổi mật khẩu', 'Tra cứu', 'Tư vấn trực tuyến', 'Đăng xuất']
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    # ================================= Log in ============================== #
    if not st.session_state.logged_in:
        with loginForm.form('Login'):
            id = st.text_input('Mã số sinh viên', max_chars=MSSV_CHARS, placeholder='VD: 20184172')
            pw = st.text_input('Mật khẩu', max_chars=PW_CHARS, type='password')
            loginBtn = st.form_submit_button('Đăng nhập')
            resetBtn = st.form_submit_button('Quên mật khẩu?') # Just for fun

            if resetBtn:
                st.info('Coming soon :smile:')

            if loginBtn:
                if id and pw:
                    if len(id) != MSSV_CHARS: # Check length
                        st.warning(f'Mã số sinh viên phải có {MSSV_CHARS} ký tự!')
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
                            st.success('Đăng nhập thành công')
                            time.sleep(2)
                            
                            # Clear login form
                            loginForm.empty()
                        else:
                            st.error('Sai mã số sinh viên hoặc mật khẩu!')
                else:
                    st.warning('Hãy nhập mã số sinh viên hoặc mật khẩu!')
    # ================================= Log in ============================== #


    # ================================= Menus =============================== #
    if st.session_state.logged_in:
        option = menuSelection.selectbox('Menu', menus)

        if option == menus[0]:
            if not st.session_state.bg:
                bg.image(cv2.imread('bg.png'), channels='BGR')
                st.session_state.bg = True
    # ================================= Menus =============================== #
        
        # ========================= Change password ========================= #
        elif option == menus[1]:
            if not st.session_state.bg:
                bg.image(cv2.imread('bg.png'), channels='BGR')
                st.session_state.bg = True

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
                        else:
                            st.error('Đổi mật khẩu không thành công!')
                    else:
                        st.warning('Mật khẩu không hợp lệ!')
        # ========================= Change password ======================== #


        # ============================= Search ============================= #
        elif option == menus[2]:
            bg.empty()
            st.session_state.bg = False
            try:
                ClientSocket.send(pickle.dumps([103, DIR]))
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
                else:
                    _, contents, indexes = data

                    # for content in contents:
                    st.markdown('\n'.join(contents), unsafe_allow_html=True)

                    if len(indexes) > 1:
                        with st.expander("See explanation"):
                            for index in indexes[1:]:
                                st.write(index)

        # ============================= Search ============================= #


        # ============================== Chat ============================== #
        elif option == menus[3]:
            bg.empty()
            st.session_state.bg = False
            
        # ============================== Chat ============================== #


        # ============================= Log out ============================ #
        elif option == menus[4]:
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

try:
    app()
except socket.error as e:
    st.exception(e)
    ClientSocket.close()