from __init__ import HEADER, PORT, FORMAT, DISCONNECT_MESSAGE, IP_ADDR, SERVER_STATE, NUMBER_OF_CLIENTS, CYCLES
import socket
import threading
import logging
import os
import sys


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
    def send_msg(c, state):
        logging.info(f'[SENDING SERVER_STATE] Sending SERVER_STATE {state} to client')
        c.send(state.encode(FORMAT))

    def send_id_client(c, a):
        Id = str(a[1])
        logging.info(f'[SENDING ID] Sending ID {Id} to client')
        c.send(Id.encode(FORMAT))

    def send_state(c, state):
        logging.info(f'[SENDING SERVER_STATE] Sending SERVER_STATE {state} to client')
        c.send(state.encode(FORMAT))

    def receive_msg(c, a):
        try:
            msg_length = c.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = c.recv(msg_length).decode(FORMAT)
                logging.info(f'[RECEIVING] Received message from {a}: {msg}')
                return msg
        except Exception as e:
            logging.critical(f'[TIMEOUT ERROR] {e}')

    send_id_client(conn, addr)
    connected = True
    message = receive_msg(conn, addr)
    if connected:
        logging.info(f"[NEW CONNECTION]\t {addr} connected!")
    else:
        logging.info(f"[CONNECTION ERROR]\t {addr} NOT connected!")
    while connected:
        if message == DISCONNECT_MESSAGE:
            logging.info(f'[DISCONNECTING] Client {addr} is disconnecting...')
            break
        if message == 'Hello World!':
            send_state(conn, SERVER_STATE.INIT_GLOBAL_WEIGHTS)
        if message == 'READY!':
            logging.info(f'[CLIENT STATE] Client {addr} state is READY!')
        if message == 'Waiting for weights!':
            if server.cycle:
                print(server.cycle)
                send_msg(conn, 'Global Weights')
            else:
                print('Init weights')
                send_msg(conn, 'Global Weights')
        if message == 'Local Weights':
            # Do some averaging
            # message = receive_msg(conn, addr)
            if server.cycle != CYCLES:
                send_msg(conn, 'Global Weights')
                server.cycle += 1
            else:
                send_msg(conn, DISCONNECT_MESSAGE)
                break
        if message == '':
            logging.info(f'[SYSTEM ERROR] Exiting...')
            sys.exit()
        message = receive_msg(conn, addr)

    conn.close()


def cleanse():
    for file in os.listdir():
        if file[-1] == 'g':
            os.remove(file)


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
    cleanse()
    logging.basicConfig(level=logging.INFO, filename='server.log', filemode='w',
                        format='%(asctime)s - %(message)s')
    main()
