import os


def find_client_index():
    index = 0
    for file in os.listdir():
        if file[0] == 'c':
            index += 1
    return index
