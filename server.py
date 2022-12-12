from __init__ import log_cleansing, HEADER_SEND, HEADER_RECV, PORT, FORMAT, INV_FLAGS, \
    DISCONNECT_MESSAGE, IP_ADDR, NUMBER_OF_CLIENTS, CYCLES, FLAGS, INIT_WEIGHTS, TEST_SERVER_PATH
from utils import create_model
import socket
import threading
import logging
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=1 / (NUMBER_OF_CLIENTS + 4))

sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options))


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
        self.flag = ''
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

    def evaluation(self):
        test_datagen = ImageDataGenerator(
            rescale=1. / 255)
        test_generator = test_datagen.flow_from_directory(
            directory=TEST_SERVER_PATH,
            target_size=(50, 50),
            color_mode="rgb",
            batch_size=4,
            class_mode="categorical",
        )
        # Testing phase after averaging!
        self.model.compile(loss='categorical_crossentropy', optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
                           metrics=['accuracy'])
        results = self.model.evaluate(test_generator)
        logging.info(f'[TEST AFTER AVERAGING CYCLE {self.cycle}]')
        logging.info(results)

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


def AVERAGING():
    if not weights:
        return
    else:
        while weights:
            if len(weights) == 3:
                curr_weights = weights.copy()
                weights.clear()
                logging.info('[AVERAGING]')
                server.model.set_weights(
                    [np.mean(np.array([curr_weights[i][j] for i in range(len(curr_weights))]), axis=0) for j in
                     range(len(curr_weights[0]))])


def handle_client(conn, addr, flag):
    PORT_ID = str(addr[1])

    def send_msg(c, _flag, _message):
        def message_formatting(_message):
            pickled_message = pickle.dumps(_message)
            msg_bytes = bytes(''.join([FLAGS[_flag], f'{len(pickled_message):<{HEADER_SEND}}']),
                              FORMAT) + pickled_message
            return msg_bytes

        _message = message_formatting(_message)
        logging.info(f'[SENDING {_flag}] Sending {_flag} to client {PORT_ID}')
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
        logging.info(f'[RECEIVING MESSAGE FROM CLIENT {PORT_ID}]')
        return full_message, INV_FLAGS[_flag]

    if flag == '':
        send_msg(conn, 'ID', PORT_ID)
        message, flag = receive_msg(conn)
        server.flag = 'CONNECTED'
    if flag == 'CONNECTED':
        send_msg(conn, 'GLOBAL WEIGHTS', server.model.get_weights())
        message, flag = receive_msg(conn)
        logging.info(f'[LOCAL WEIGHTS FROM CLIENT {str(addr[1])}]')
        weights.append(message)
    if flag == DISCONNECT_MESSAGE:
        send_msg(conn, DISCONNECT_MESSAGE, DISCONNECT_MESSAGE)
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
        thread = threading.Thread(target=handle_client, args=(conn, addr, server.flag))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    while server.cycle <= CYCLES - 1:
        if server.cycle == CYCLES - 1:
            server.flag = DISCONNECT_MESSAGE
        AVERAGING()
        '''
            TO DO:
            Add testing phase (global model) after averaging the weights.
            
            CANT DO EVALUATION 
            !!! OOM GPU !!!
        '''
        # server.evaluation()
        threads.clear()
        for connection in connections:
            thread = threading.Thread(target=handle_client, args=(*connection, server.flag))
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        server.cycle += 1


if __name__ == '__main__':
    log_cleansing()
    logging.basicConfig(level=logging.INFO, filename='server.log', filemode='w',
                        format='%(message)s')
    main()
