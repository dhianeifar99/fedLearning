from __init__ import log_cleansing_client, HEADER_SEND, HEADER_RECV, INV_FLAGS,\
    PORT, FORMAT, IP_ADDR, DISCONNECT_MESSAGE, FLAGS
from utils import find_client_index, create_model
import socket
import logging
import pickle

log_cleansing_client()
INDEX = find_client_index()

logging.basicConfig(level=logging.INFO, filename=f'client{INDEX}.log', filemode='w',
                    format='%(message)s')


class Client:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.model = create_model('LOCAL_MODEL')

    def connecting(self):
        logging.info('[CONNECTING] Connecting...')
        self.client_socket.connect((self.addr, self.port))

    def send_msg(self, _flag, _message):
        def message_formatting(_message):
            pickled_message = pickle.dumps(_message)
            msg_bytes = bytes(''.join([FLAGS[_flag], f'{len(pickled_message):<{HEADER_SEND}}']),
                              FORMAT) + pickled_message
            return msg_bytes

        _message = message_formatting(_message)
        logging.info(f'[SENDING {_flag}] Sending {_flag} to client')
        self.client_socket.send(_message)

    def receive_msg(self):
        l = []
        received_message = self.client_socket.recv(HEADER_RECV)
        HEADER = received_message.decode(FORMAT)
        _flag = HEADER[0]
        message_length = int(HEADER[1:])
        l.append(received_message)
        len_l = len(received_message)
        while True:
            received_message = self.client_socket.recv(HEADER_RECV)
            l.append(received_message)
            len_l += len(received_message)
            if len_l - HEADER_RECV == message_length:
                break
        full_message = b''.join(l)
        full_message = pickle.loads(full_message[HEADER_RECV:])
        logging.info(f'[RECEIVING MESSAGE]')
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
            logging.info('[GOT GLOBAL WEIGHTS]')
            client.model.set_weights(message)
            # Train

            client.send_msg('LOCAL WEIGHTS', client.model.get_weights())
        if flag == DISCONNECT_MESSAGE:
            break


if __name__ == '__main__':
    main()
