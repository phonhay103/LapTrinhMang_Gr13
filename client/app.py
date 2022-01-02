import socket
import streamlit as st
import cv2
import time
import pyautogui

from config import *
from account import *

import pickle # TEMP #

ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    ClientSocket.connect((HOST, PORT))
except socket.error as e:
    exit()

def app():
    st.title("Sổ tay sinh viên 2021")
    bg = st.empty()
    bg.image(cv2.imread('bg.png'), channels='BGR')
    menus = ['Trang chủ', 'Đổi mật khẩu', 'Tra cứu', 'Tư vấn trực tuyến', 'Đăng xuất']

    # ================================= Log in ============================== #
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        containers = [st.sidebar.empty() for i in range(5)]
        id = containers[0].text_input('Mã số sinh viên', max_chars=MSSV_CHARS, placeholder='VD: 20184172')
        pw = containers[1].text_input('Mật khẩu', max_chars=PW_CHARS, type='password')
        loginBtn = containers[2].button('Đăng nhập')
        resetBtn = containers[3].button('Quên mật khẩu?') # Just for fun

        if resetBtn:
            containers[4].info('Coming soon :smile:')

        if loginBtn:
            if id and pw:
                if len(id) != MSSV_CHARS: # Check length
                    containers[4].warning(f'Mã số sinh viên phải có {MSSV_CHARS} ký tự!')
                else: # Send to server 
                    data = get_login_data(id, pw)
                    try:
                        ClientSocket.send(data)
                        status = ClientSocket.recv(1024)
                    except:
                        status = pickle.dumps([500, 'Error']) # TEMP #
    
                    if get_login_status(status):
                        st.session_state.logged_in = True
                        st.session_state.id = id
                        containers[4].success('Đăng nhập thành công')
                        time.sleep(1)
                        for container in containers:
                            container.empty()
                    else:
                        containers[4].error('Sai mã số sinh viên hoặc mật khẩu!')
            else:
                containers[4].warning('Hãy nhập mã số sinh viên hoặc mật khẩu!')
    # ================================= Log in ============================== #


    # ================================= Menus =============================== #
    options = st.sidebar.empty()
    option = menus[0]
    if st.session_state.logged_in:
        if option == menus[0]:
            option = options.selectbox('Menu', menus, index=0)
        else:
            option = options.selectbox('Menu', menus)
    # ================================= Menus =============================== #


        # ============================ Homepage ============================= #
        if option == menus[0]:
            bg.image(cv2.imread('bg.png'), channels='BGR')
        # ============================ Homepage ============================= #


        # ========================= Change password ========================= #
        if option == menus[1]:
            bg.image(cv2.imread('bg.png'), channels='BGR')
            containers = [st.sidebar.empty() for i in range(4)]
            new_pw_1 = containers[0].text_input('Mật khẩu mới:', max_chars=PW_CHARS)
            new_pw_2 = containers[1].text_input('Xác nhận mật khẩu mới:', max_chars=PW_CHARS)
            changeBtn = containers[2].button('Đổi mật khẩu')

            if changeBtn:
                data = get_change_password_data(st.session_state.id, new_pw_1, new_pw_2)
                if data:  # Send to server 
                    # ClientSocket.send(data)
                    # status = ClientSocket.recv(1024) # Blocking ?
                    status = pickle.dumps([200, 'Success']) # TEMP #
                    if get_change_password_status(status):
                        # Remove widgets
                        containers[3].success('Đổi mật khẩu thành công')
                        time.sleep(1)
                        for container in containers:
                            container.empty()
                        
                        # To homepage
                        option == options[0]
                    else:
                        containers[3].error('Đổi mật khẩu không thành công!')
                else:
                    containers[3].warning('Mật khẩu không hợp lệ!')
        # ========================= Change password ======================== #


        # ============================= Search ============================= #
        if option == menus[2]:
            bg.empty()
            pass
        # ============================= Search ============================= #


        # ============================== Chat ============================== #
        if option == menus[3]:
            bg.empty()
            pass
        # ============================== Chat ============================== #


        # ============================= Log out ============================ #
        if option == menus[4]:
            container = st.sidebar.empty()
            data = get_logout_data(st.session_state.id)
            # ClientSocket.send(data)
            # status = ClientSocket.recv(1024) # Blocking ?
            status = pickle.dumps([200, 'S']) # TEMP #
            if get_logout_status(status):
                st.session_state.logged_in = False
                del st.session_state['id']
                container.success('Đăng xuất thành công')
                time.sleep(1)
                container.empty()
                pyautogui.press('f5')
            else:
                container.error('Đăng xuất không thành công!')
        # ============================= Log out ============================ #

try:
    app()
except socket.error as e:
    st.text(e)
    ClientSocket.close()
    exit()