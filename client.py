from __init__ import HEADER_SEND, HEADER_RECV, INV_FLAGS,\
    PORT, FORMAT, IP_ADDR, DISCONNECT_MESSAGE, FLAGS, CLIENT_PATH
from utils import find_client_index, create_model
import socket
import logging
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os


INDEX = find_client_index()
print(INDEX)

logging.basicConfig(level=logging.INFO, filename=f'client{INDEX}.log', filemode='w',
                    format='%(message)s')


class Client:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.model = create_model('LOCAL_MODEL')
        self.model.compile(loss='categorical_crossentropy', optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), metrics=['accuracy'])

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
        logging.info(f'[SENDING {_flag}] SENDING {_flag} TO SERVER')
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

            # train
            client.model.set_weights(message)
            train_generator = train_datagen.flow_from_directory(
                directory=os.path.join(CLIENT_PATH, str(INDEX), 'train'),
                target_size=(50, 50),
                color_mode="rgb",
                batch_size=16,
                class_mode="categorical",
            )

            val_generator = val_datagen.flow_from_directory(
                directory=os.path.join(CLIENT_PATH, str(INDEX), 'val'),
                target_size=(50, 50),
                color_mode="rgb",
                batch_size=16,
                class_mode="categorical",
            )

            STEP_SIZE_TRAIN = train_generator.n // train_generator.batch_size
            STEP_SIZE_VALID = val_generator.n // val_generator.batch_size
            history = client.model.fit_generator(train_generator,
                                                 steps_per_epoch=STEP_SIZE_TRAIN,
                                                 validation_data=val_generator,
                                                 validation_steps=STEP_SIZE_VALID,
                                                 epochs=3)
            weights = client.model.get_weights()
            # pickle.dump(weights, open(f'client{INDEX}.pkl', 'wb'))
            logging.info(history.history)
            client.send_msg('LOCAL WEIGHTS', weights)
        if flag == DISCONNECT_MESSAGE:
            break


if __name__ == '__main__':

    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        shear_range=0.2,
        zoom_range=0.2,)
    val_datagen = ImageDataGenerator(
        rescale=1. / 255)

    main()
