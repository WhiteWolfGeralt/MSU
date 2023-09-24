import numpy as np

class Preprocesser:
    def __init__(self):
        pass

    def fit(self, X, Y=None):
        pass

    def transform(self, X):
        pass

    def fit_transform(self, X, Y=None):
        pass


class MyOneHotEncoder(Preprocesser):
    codes = []

    def __init__(self, dtype=np.float64):
        super(Preprocesser).__init__()
        self.dtype = dtype

    def fit(self, X, Y=None):
        """
        param X: training objects, pandas-dataframe, shape [n_objects, n_features]
        param Y: unused
        """
        self.codes = []
        for col in X:
            values = sorted(list(set(X[col])))
            self.codes.append(dict(zip(values, np.identity(len(values), int))))
        pass

    def transform(self, X):
        """
        param X: objects to transform, pandas-dataframe, shape [n_objects, n_features]
        returns: transformed objects, numpy-array, shape [n_objects, |f1| + |f2| + ...]
        """
        ret = []
        for i, row in X.iterrows():
            index = 0
            encode = []
            for item in row:
                encode.extend(self.codes[index][item])
                index += 1
            ret.append(encode)
        return np.array(ret)

    def fit_transform(self, X, Y=None):
        self.fit(X)
        return self.transform(X)

    def get_params(self, deep=True):
        return {"dtype": self.dtype}


class SimpleCounterEncoder:
    counters = dict()

    def __init__(self, dtype=np.float64):
        self.dtype=dtype

    def fit(self, X, Y):
        """
        param X: training objects, pandas-dataframe, shape [n_objects, n_features]
        param Y: target for training objects, pandas-series, shape [n_objects,]
        param a: constant for counters, float
        param b: constant for counters, float
        for col in range(X.shape[1]):
        """
        for col in X:
            attrs = sorted(list(set(X[col])))
            add = dict()
            for attr in attrs:
                mask = (X[col] == attr)
                Y_masked = list(Y[mask])
                add[attr] = np.array([np.sum(Y_masked) / len(X[col][mask]), len(X[col][mask]) / len(X[col])])
            self.counters[col] = add
        pass

    def transform(self, X, a=1e-5, b=1e-5):
        """
        param X: objects to transform, pandas-dataframe, shape [n_objects, n_features]
        returns: transformed objects, numpy-array, shape [n_objects, 3]
        """
        ret = [[] for _ in range(X.shape[0])]
        for col in X:
            attrs = list(X[col])
            code = self.counters[col]
            for i in range(len(attrs)):
                successes, counters = code[attrs[i]][0], code[attrs[i]][1]
                ret[i].extend(np.array([successes, counters, (successes + a) / (counters + b)]))
        return np.array(ret)

    def fit_transform(self, X, Y, a=1e-5, b=1e-5):
        self.fit(X, Y)
        return self.transform(X, Y)

    def get_params(self, deep=True):
        return {"dtype": self.dtype}


def group_k_fold(size, n_splits=3, seed=1):
    idx = np.arange(size)
    np.random.seed(seed)
    idx = np.random.permutation(idx)
    n_ = size // n_splits
    for i in range(n_splits - 1):
        yield idx[i * n_: (i + 1) * n_], np.hstack((idx[:i * n_], idx[(i + 1) * n_:]))
    yield idx[(n_splits - 1) * n_:], idx[:(n_splits - 1) * n_]

class FoldCounters:
    Y, groups = 0, []

    def __init__(self, n_folds=3, dtype=np.float64):
        self.dtype = dtype
        self.n_folds = n_folds
        self.y = 0
        self.data = []

    def fit(self, X, Y, seed=1):
        """
        param X: training objects, pandas-dataframe, shape [n_objects, n_features]
        param Y: target for training objects, pandas-series, shape [n_objects,]
        param a: constant for counters, float
        param b: constant for counters, float
        param seed: random seed, int
        """
        self.y = Y
        for i in group_k_fold(X.shape[0], self.n_folds, seed):
            self.data.append((i[0], i[1]))

    def transform(self, X, a=1e-5, b=1e-5):
        """
        param X: objects to transform, pandas-dataframe, shape [n_objects, n_features]
        returns: transformed objects, numpy-array, shape [n_objects, 3]
        """
        result = dict()
        for i in range(self.n_folds):
            transform_X = X.loc[self.data[i][0], :]
            fit_X = X.loc[self.data[i][1], :]
            Y = self.y[self.data[i][1]]
            counter = SimpleCounterEncoder()
            counter.fit(fit_X, Y)
            res = counter.transform(transform_X, a, b)
            for j in range(len(transform_X)):
                ls = list(transform_X.index)
                result[ls[j]] = res[j, :]
        sorted_tuple = list(dict(sorted(result.items(), key=lambda x: x[0])).values())
        return np.vstack(sorted_tuple)

    def fit_transform(self, X, Y, a=1e-5, b=1e-5):
        self.fit(X, Y)
        return self.transform(X, Y)


def weights(x, y):
    """
    param x: training set of one feature, numpy-array, shape [n_objects,]
    param y: target for training objects, numpy-array, shape [n_objects,]
    returns: optimal weights, numpy-array, shape [|x unique values|,]
    """
    one_hot = {attr: 0 for attr in sorted(list(set(x)))}
    y = list(zip(x, y))
    for attr in one_hot.keys():
        one_hot[attr] = y.count((attr, 1)) / list(x).count(attr)
    return np.array(list(one_hot.values()))
