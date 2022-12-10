from __init__ import log_cleansing, HEADER_SEND, HEADER_RECV, PORT, FORMAT, INV_FLAGS, \
    DISCONNECT_MESSAGE, IP_ADDR, NUMBER_OF_CLIENTS, CYCLES, FLAGS, INIT_WEIGHTS
from utils import create_model
import socket
import threading
import logging
import sys
import pickle
import numpy as np


class Server:
    def __init__(self, addr, port, n_clients=NUMBER_OF_CLIENTS):
        logging.info("[STARTING]\t\t server is starting...")
        self.addr = addr
        self.port = port
        self.clients = n_clients
        self.curr_n_clients = 0
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cycle = 0
        self.model = create_model('Global_Model')
        with open(INIT_WEIGHTS, 'rb') as pickle_file:
            self.model.set_weights(pickle.load(pickle_file))
        logger = logging.getLogger('server.log')
        logging.info("[GLOBAL MODEL SUMMARY]")
        self.model.summary(print_fn=logger.info)

        try:
            self.server.bind((self.addr, self.port))

        except socket.error as e:
            print(str(e))

    def listening(self):
        logging.info(f"[LISTENING]\t\t server is listening on {self.addr}!")
        self.server.listen()

    def verif_n_clients(self):
        def deny_log():
            logging.info('[SATURATION] REACHED MAXIMUM CAPACITY!')
            return 0

        def allow_log():
            logging.info(f'[ACCEPTING CONNECTION] {self.clients - self.curr_n_clients} clients left!')
            return 1

        return allow_log() if self.curr_n_clients < self.clients else deny_log()

    def accepting(self):
        self.curr_n_clients += 1
        return self.server.accept()


def handle_client(conn, addr):
    def send_msg(c, _flag, _message):
        def message_formatting(_message):
            pickled_message = pickle.dumps(_message)
            msg_bytes = bytes(''.join([FLAGS[_flag], f'{len(pickled_message):<{HEADER_SEND}}']),
                              FORMAT) + pickled_message
            return msg_bytes

        _message = message_formatting(_message)
        logging.info(f'[SENDING {_flag}] Sending {_flag} to client {str(addr[1])}')
        c.send(_message)

    def receive_msg(_conn):
        l = []
        received_message = _conn.recv(HEADER_RECV)
        HEADER = received_message.decode(FORMAT)
        _flag = HEADER[0]
        message_length = int(HEADER[1:])
        l.append(received_message)
        len_l = len(received_message)
        while True:
            received_message = _conn.recv(HEADER_RECV)
            l.append(received_message)
            len_l += len(received_message)
            if len_l - HEADER_RECV == message_length:
                break
        full_message = b''.join(l)
        full_message = pickle.loads(full_message[HEADER_RECV:])
        logging.info(f'[RECEIVING MESSAGE FROM CLIENT {str(addr[1])}]')
        return full_message, INV_FLAGS[_flag]

    send_msg(conn, 'ID', str(addr[1]))
    connected = True
    message, flag = receive_msg(conn)
    while connected:
        if flag == 'CONNECTED':
            send_msg(conn, 'GLOBAL WEIGHTS', server.model.get_weights())
        if flag == 'LOCAL WEIGHTS':
            logging.info(f'[LOCAL WEIGHTS FROM CLIENT {str(addr[1])}]')
            weights.append(message)
            # Do some averaging

            logging.info('[AVERAGING]')
            # Averaging
            server.model.set_weights([np.mean(np.array([weights[i][j] for i in range(len(weights))]), axis=0) for j in
                                      range(len(weights[0]))])
            weights.clear()
            # Add GLOBAL MODEL results on test data to log
            if server.cycle < CYCLES - 1:
                send_msg(conn, 'GLOBAL WEIGHTS', server.model.get_weights())
                server.cycle += 1
            else:
                send_msg(conn, DISCONNECT_MESSAGE, DISCONNECT_MESSAGE)
                sys.exit()
        message, flag = receive_msg(conn)

    conn.close()


def main():
    global server
    server = Server(IP_ADDR, PORT)
    server.listening()
    global weights
    weights = []
    threads = []
    connections = []
    while server.verif_n_clients():
        conn, addr = server.accepting()
        connections.append((conn, addr))
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        threads.append(thread)
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    log_cleansing()
    logging.basicConfig(level=logging.INFO, filename='server.log', filemode='w',
                        format='%(message)s')
    main()
