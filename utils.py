import os


def find_client_index():
    index = 1
    for file in os.listdir():
        if file[0] == 'c' and file[-1] == 'g':
            index += 1
    return index
