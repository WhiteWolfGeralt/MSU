import os

from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

import numpy as np
import pandas as pd

class PotentialTransformer:
    """
    A potential transformer.

    This class is used to convert the potential's 2d matrix to 1d vector of features.
    """

    def fit(self, x, y):
        """
        Build the transformer on the training set.
        :param x: list of potential's 2d matrices
        :param y: target values (can be ignored)
        :return: trained transformer
        """
        return self

    def fit_transform(self, x, y):
        """
        Build the transformer on the training set and return the transformed dataset (1d vectors).
        :param x: list of potential's 2d matrices
        :param y: target values (can be ignored)
        :return: transformed potentials (list of 1d vectors)
        """
        return self.transform(x)

    def move(self, x):
        test = pd.DataFrame(x)
        list_column = []
        list_row = []
        for i in range(256):
            if np.min(test.iloc[i]) <= 2:
                list_row.append(i)
        for i in range(256):
            if np.min(test.iloc[:, i]) <= 2:
                list_column.append(i)
        pos_column = round((list_column[-1] + list_column[0]) / 2)
        pos_row = round((list_row[-1] + list_row[0]) / 2)
        test = np.roll(test, 128 - pos_row, axis=0)
        test = np.roll(test, 128 - pos_column, axis=1)
        return test

    def transform(self, x):
        """
        Transform the list of potential's 2d matrices with the trained transformer.
        :param x: list of potential's 2d matrices
        :return: transformed potentials (list of 1d vectors)
        """
        for i in range(0, len(x)):
            x[i] = self.move(x[i])
        return x.reshape((x.shape[0], -1))

def load_dataset(data_dir):
    """
    Read potential dataset.

    This function reads dataset stored in the folder and returns three lists
    :param data_dir: the path to the potential dataset
    :return:
    files -- the list of file names
    np.array(X) -- the list of potential matrices (in the same order as in files)
    np.array(Y) -- the list of target value (in the same order as in files)
    """
    files, X, Y = [], [], []
    for file in os.listdir(data_dir):
        potential = np.load(os.path.join(data_dir, file))
        files.append(file)
        X.append(potential["data"])
        Y.append(potential["target"])
    return files, np.array(X), np.array(Y)

def train_model_and_predict(train_dir, test_dir):
    _, X_train, Y_train = load_dataset(train_dir)
    test_files, X_test, _ = load_dataset(test_dir)
    # it's suggested to modify only the following line of this function
    transform = PotentialTransformer()
    X_train = transform.transform(X_train)
    X_test = transform.transform(X_test)
    regressor = ExtraTreesRegressor(n_estimators=300, n_jobs=-1, criterion="mae")
    param_grid = {
        'max_depth': range(30, 71, 5),
        'max_features': range(30, 91, 10),
    }
    search = GridSearchCV(regressor, param_grid, cv=3, n_jobs=-1)
    search.fit(X_train, Y_train)

    best = ExtraTreesRegressor(n_estimators=3000,
                               max_depth=search.best_params_['max_depth'],
                               max_features=search.best_params_['max_features'],
                               n_jobs=-1,
                               criterion="mae")
    best.fit(X_train, Y_train)
    predictions = best.predict(X_test)
    return {file: value for file, value in zip(test_files, predictions)}


