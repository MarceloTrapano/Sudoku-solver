from keras.src.legacy.preprocessing.image import ImageDataGenerator
from keras.preprocessing import image 
from keras.optimizers import RMSprop
from keras.datasets import mnist
import tensorflow as tf
import cv2
import os
import numpy as np

mnist.load_data()
train = ImageDataGenerator(rescale = 1/255)
validation = ImageDataGenerator(rescale = 1/255)
train_dataset = train.flow_from_directory('Training/',
                                          batch_size=30,
                                          class_mode='binary')
validation_dataset = validation.flow_from_directory('Validation/',
                                          batch_size=30,
                                          class_mode='binary')
print(train_dataset)
