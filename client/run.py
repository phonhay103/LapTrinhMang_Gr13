import subprocess
from multiprocessing import Process, Manager

def run_client_socket():
    subprocess.call("python a.py")

def run_client_GUI():
    subprocess.call("python b.py")

run_client_socket()
run_client_GUI()