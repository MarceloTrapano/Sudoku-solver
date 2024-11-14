import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import random
import pickle
from typing import List, Any

CATEGORIES: List[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
DATA_DIR: str = 'C:/Users/gt/Desktop/Studbaza/Sudoku_sol/Training'
IMG_SIZE: int = 25

training_data: List[Any] = []

for category in CATEGORIES:
    path: str = os.path.join(DATA_DIR, str(category))
    for img in os.listdir(path):
        img_array = cv2.imread(os.path.join(path, img), cv2.IMREAD_GRAYSCALE)
        new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
        training_data.append([new_array, category])

random.shuffle(training_data)

X: List[Any] = []
y: List[Any] = []

for features, label in training_data:
    X.append(features)
    y.append(label)

X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
print(X[0].shape)
plt.imshow(X[0])
plt.show()

y = np.array(y)
print(y.shape)

pickle_out = open("X.pickle", "wb")
pickle.dump(X, pickle_out)
pickle_out.close()

pickle_out = open("y.pickle", "wb")
pickle.dump(y, pickle_out)
pickle_out.close()