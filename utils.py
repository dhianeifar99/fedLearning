import os
from tensorflow.keras import layers, models


def create_model(name):
    model = models.Sequential(name=name)
    model.add(layers.InputLayer(input_shape=(224, 224, 3), name=f'{name}_input_layer'))
    model.add(layers.Conv2D(16, (3, 3), activation='relu', name=f'{name}_Conv2D_1'))
    model.add(layers.MaxPooling2D((2, 2), name=f'{name}_MaxPool2D_1'))
    model.add(layers.Conv2D(32, (3, 3), activation='relu', name=f'{name}_Conv2D_2'))
    model.add(layers.MaxPooling2D((2, 2), name=f'{name}_MaxPool2D_2'))
    model.add(layers.Conv2D(64, (3, 3), activation='relu', name=f'{name}_Conv2D_3'))
    model.add(layers.MaxPooling2D((2, 2), name=f'{name}_MaxPool2D_3'))
    model.add(layers.Conv2D(128, (3, 3), activation='relu', name=f'{name}_Conv2D_4'))
    model.add(layers.MaxPooling2D((2, 2), name=f'{name}_MaxPool2D_4'))
    model.add(layers.Conv2D(256, (3, 3), activation='relu', name=f'{name}_Conv2D_5'))
    model.add(layers.MaxPooling2D((2, 2), name=f'{name}_MaxPool2D_5'))
    model.add(layers.Conv2D(512, (3, 3), activation='relu', name=f'{name}_Conv2D_6'))
    model.add(layers.MaxPooling2D((2, 2), name=f'{name}_MaxPool2D_6'))
    model.add(layers.Flatten(name=f'{name}_Flatten'))
    model.add(layers.Dense(128, activation='relu', name=f'{name}_Dense_1'))
    model.add(layers.Dense(512, activation='relu', name=f'{name}_Dense_2'))
    model.add(layers.Dense(4, activation='sigmoid', name=f'{name}_Output'))
    return model


def find_client_index():
    index = 1
    for file in os.listdir():
        if file[0] == 'c' and file[-1] == 'g':
            index += 1
    return index
