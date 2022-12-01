from __init__ import log_cleansing_client, HEADER_SEND, HEADER_RECV, INV_FLAGS,\
    PORT, FORMAT, IP_ADDR, DISCONNECT_MESSAGE, FLAGS
from utils import find_client_index
import socket
import logging
import pickle

log_cleansing_client()

logging.basicConfig(level=logging.INFO, filename=f'client{find_client_index()}.log', filemode='w',
                    format='%(asctime)s - %(message)s')


class Client:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_state = ''
        self.id = ''

    def connecting(self):
        logging.info('[CONNECTING] Connecting...')
        self.client_socket.connect((self.addr, self.port))

    def send_msg(self, msg, _flag):
        def message_formatting(_message):
            pickled_message = pickle.dumps(_message)
            msg_bytes = bytes(''.join([FLAGS[_flag], f'{len(pickled_message):<{HEADER_SEND}}']), FORMAT) + pickled_message
            return msg_bytes

        _message = message_formatting(msg)
        logging.info(f'[SENDING {_flag}] Sending {_flag} {msg} to client')
        self.client_socket.send(_message)

    def receive_msg(self):
        full_message = b''
        received_message = self.client_socket.recv(HEADER_RECV)
        HEADER = received_message.decode(FORMAT)
        _flag = HEADER[0]
        message_length = int(HEADER[1:])
        full_message += received_message
        while True:
            received_message = self.client_socket.recv(HEADER_RECV)
            full_message += received_message
            if len(full_message) - HEADER_RECV == message_length:
                break
        full_message = pickle.loads(full_message[HEADER_RECV:])
        logging.info(f'[RECEIVING MESSAGE] {full_message}')
        return full_message, INV_FLAGS[_flag]


def main():
    client = Client(IP_ADDR, PORT)
    client.connecting()
    client.receive_msg()
    client.send_msg('CONNECTED', 'CONNECTED')
    connected = True
    while connected:
        message, flag = client.receive_msg()
        if flag == 'GLOBAL WEIGHTS':
            # Training
            logging.info('[GOT GLOBAL WEIGHTS]')
            client.send_msg('LOCAL WEIGHTS', 'LOCAL WEIGHTS')
        if flag == DISCONNECT_MESSAGE:
            break


if __name__ == '__main__':
    main()
