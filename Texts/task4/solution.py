import pickle
import json
import numpy as np
import scipy

saved_file = "KNN_model.pkl"
saved_vectorizer = "vectorizer.pkl"

class Solution:
    def __init__(self):
        with open(saved_file, "rb") as file:
            self.model = pickle.load(file)

        with open(saved_vectorizer, "rb") as file:
            self.vectorizer = pickle.load(file)

        with open('dev-dataset-task2022-04.json') as f:
            raw_data = json.load(f)
        X_data, y_data = [], []
        for pair in raw_data:
            X_data.append(pair[0])
            y_data.append(int(pair[1]))
        self.X_train = self.vectorizer.transform(np.array(X_data))
        self.y_train = np.array(y_data)

    def predict(self, text: str) -> str:
        data = self.vectorizer.transform([text])
        pred = self.model.predict(data)

        self.X_train = scipy.sparse.vstack([self.X_train, data])
        self.y_train = np.concatenate([self.y_train, pred])

        self.model.fit(self.X_train, self.y_train)
        return str(pred[0])
