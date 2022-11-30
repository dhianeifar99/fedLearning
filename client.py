from __init__ import HEADER, PORT, FORMAT, IP_ADDR, DISCONNECT_MESSAGE
from utils import find_client_index
import socket
import logging

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

    def send_msg(self, msg):
        logging.info(f'[SENDING] Sending message {msg} to server')
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.client_socket.send(send_length)
        self.client_socket.send(message)

    def receive_id(self):
        ID = self.client_socket.recv(HEADER).decode(FORMAT)
        logging.info(f'[RECEIVING ID] receiving ID {ID} from server')
        self.id = ID

    def receive_message(self):
        message = self.client_socket.recv(HEADER).decode(FORMAT)
        logging.info(f'[RECEIVING MESSAGE] receiving message {message} from server')
        return message

    def receive_server_state(self):
        msg = self.client_socket.recv(HEADER).decode(FORMAT)
        logging.info(f'[RECEIVING SERVER_STATE] receiving SERVER_STATE {msg} from server')
        self.server_state = msg


def main():
    client = Client(IP_ADDR, PORT)
    client.connecting()
    client.receive_id()
    client.send_msg('Hello World!')
    connected = True
    while connected:
        message = client.receive_message()
        if message == 'INIT_GLOBAL_WEIGHTS':
            client.send_msg('Waiting for weights!')
        if message == 'Global Weights':
            # Training
            # Send weights
            client.send_msg('Local Weights')
        if message == DISCONNECT_MESSAGE:
            break
    # client.send_msg('READY!')
    # client.send_msg(DISCONNECT_MESSAGE)


if __name__ == '__main__':
    main()
