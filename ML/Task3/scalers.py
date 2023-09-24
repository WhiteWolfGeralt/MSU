import numpy as np


class MinMaxScaler:
    def __init__(self):
        self.min = 0
        self.max = 0

    def fit(self, data):
        """
        Store calculated statistics
        Parameters:
        data (np.array): train set, size (num_obj, num_features)
        """
        self.min, self.max = np.amin(data, axis=0), np.amax(data, axis=0)

    def transform(self, data):
        """
        Parameters:
        data (np.array): train set, size (num_obj, num_features)
        Return:
        np.array: scaled data, size (num_obj, num_features)
        """
        return (data - self.min) / (self.max - self.min)


class StandardScaler:
    def __init__(self):
        self.expected = 0
        self.dispersion = 0

    def fit(self, data):
        """Store calculated statistics
        Parameters:
        data (np.array): train set, size (num_obj, num_features)
        """
        self.expected = np.sum(data, axis=0) / data.shape[0]
        self.dispersion = np.std(data, axis=0)

    def transform(self, data):
        """
        Parameters:
        data (np.array): train set, size (num_obj, num_features)
        Return:
        np.array: scaled data, size (num_obj, num_features)
        """
        return (data - self.expected) / self.dispersion
