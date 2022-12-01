from __init__ import log_cleansing_server, HEADER_SEND, HEADER_RECV, PORT, FORMAT, INV_FLAGS,\
    DISCONNECT_MESSAGE, IP_ADDR, NUMBER_OF_CLIENTS, CYCLES, FLAGS
import socket
import threading
import logging
import sys
import pickle


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
            msg_bytes = bytes(''.join([FLAGS[_flag], f'{len(pickled_message):<{HEADER_SEND}}']), FORMAT) + pickled_message
            return msg_bytes

        _message = message_formatting(_message)
        logging.info(f'[SENDING {_flag}] Sending {_flag} to client')
        c.send(_message)

    def receive_msg(_conn):
        full_message = b''
        received_message = _conn.recv(HEADER_RECV)
        HEADER = received_message.decode(FORMAT)
        _flag = HEADER[0]
        message_length = int(HEADER[1:])
        full_message += received_message
        while True:
            received_message = _conn.recv(HEADER_RECV)
            full_message += received_message
            if len(full_message) - HEADER_RECV == message_length:
                break
        full_message = pickle.loads(full_message[HEADER_RECV:])
        logging.info(f'[RECEIVING MESSAGE] {full_message}')
        return full_message, INV_FLAGS[_flag]

    send_msg(conn, 'ID', str(addr[1]))
    connected = True
    message, flag = receive_msg(conn)
    while connected:
        if flag == 'CONNECTED':
            send_msg(conn, 'GLOBAL WEIGHTS', 'GLOBAL WEIGHTS')
        if flag == 'LOCAL WEIGHTS':
            logging.info(f'[LOCAL WEIGHTS]')
            # Do some averaging
            # message = receive_msg(conn, addr)
            if server.cycle < CYCLES - 1:
                send_msg(conn, 'GLOBAL WEIGHTS', 'GLOBAL WEIGHTS')
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
    connections = []
    threads = []
    while server.verif_n_clients():
        conn, addr = server.accepting()
        connections.append((conn, addr))
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        threads.append(thread)
    for thread in threads:
        thread.start()
        thread.join()


if __name__ == '__main__':
    log_cleansing_server()
    logging.basicConfig(level=logging.INFO, filename='server.log', filemode='w',
                        format='%(asctime)s - %(message)s')
    main()
