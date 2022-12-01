import os


def log_cleansing_server():
    for file in os.listdir():
        if file[0] == 's' and file[-1] == 'g':
            os.remove(file)


def log_cleansing_client():
    for file in os.listdir():
        if file[0] == 'c' and file[-1] == 'g':
            os.remove(file)


HEADER_SEND = 10
HEADER_RECV = 11
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
IP_ADDR = '192.168.173.194'
NUMBER_OF_CLIENTS = 1
CYCLES = 3
FLAGS = {
    'ID': '0',
    'CONNECTED': '1',
    'GLOBAL WEIGHTS': '2',
    'LOCAL WEIGHTS': '3',
    '!DISCONNECT': '4',
}
INV_FLAGS = {
    '0': 'ID',
    '1': 'CONNECTED',
    '2': 'GLOBAL WEIGHTS',
    '3': 'LOCAL WEIGHTS',
    '4': '!DISCONNECT',
}
