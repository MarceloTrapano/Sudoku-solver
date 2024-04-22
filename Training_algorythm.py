from keras.src.legacy.preprocessing.image import ImageDataGenerator
from keras.preprocessing import image 
from keras.optimizers import RMSprop
import tensorflow as tf
import cv2
import os
import numpy as np

train = ImageDataGenerator(rescale = 1/255)
validation = ImageDataGenerator(rescale = 1/255)
train_dataset = train.flow_from_directory('Training/',
                                          batch_size=30,
                                          class_mode='binary')
validation_dataset = validation.flow_from_directory('Validation/',
                                          batch_size=30,
                                          class_mode='binary')
model = tf.keras.models.Sequential([tf.keras.layers.Conv2D(16,(3,3),activation = 'relu',input_shape = (72,72,3)),
                                     tf.keras.layers.MaxPool2D(2,2),
                                     tf.keras.layers.Conv2D(32,(3,3),activation = 'relu'),
                                     tf.keras.layers.MaxPool2D(2,2),
                                     tf.keras.layers.Conv2D(64,(3,3),activation = 'relu'),
                                     tf.keras.layers.MaxPool2D(2,2),
                                     tf.keras.layers.Flatten(),
                                     tf.keras.layers.Dense(512,activation = 'relu'),
                                     tf.keras.layers.Dense(1,activation = 'sigmoid')])
model.compile(loss='binary_crossentropy',
              optimizer= RMSprop(learning_rate=0.001),
              metrics = ['accuracy'])
model_fit = model.fit(train_dataset,
                      steps_per_epoch = 5,
                      epochs = 30,
                      validation_data = validation_dataset)