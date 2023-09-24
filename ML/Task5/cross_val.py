import numpy as np
from collections import defaultdict

def kfold_split(num_objects, num_folds):
    """
    Split [0, 1, ..., num_objects - 1] into equal num_folds folds (last fold can be longer) and returns num_folds train-val
       pairs of indexes.

    Parameters:
    num_objects (int): number of objects in train set
    num_folds (int): number of folds for cross-validation split

    Returns:
    list((tuple(np.array, np.array))): list of length num_folds, where i-th element of list contains tuple of 2 numpy arrays,
                                       the 1st numpy array contains all indexes without i-th fold while the 2nd one contains
                                       i-th fold
    """
    partition = []
    size = num_objects // num_folds
    for i in range(0, num_folds - 1):
        partition.append(list(range(i * size, (i + 1) * size)))
    partition.append(list(range(partition[-1][-1] + 1, num_objects)))

    ret = []
    for part in partition:
        ret.append([np.concatenate((np.arange(0, part[0]), np.arange(part[-1] + 1, num_objects))),
                    np.arange(part[0], part[-1] + 1)])
    return ret


def knn_cv_score(x, y, parameters, score_function, folds, knn_class):
    """
    Takes train data, counts cross-validation score over grid of parameters (all possible parameters combinations)

    Parameters:
    X (2d np.array): train set
    y (1d np.array): train labels
    parameters (dict): dict with keys from {n_neighbors, metrics, weights, normalizers}, values of type list,
                       parameters['normalizers'] contains tuples (normalizer, normalizer_name), see parameters
                       example in your jupyter notebook
    score_function (callable): function with input (y_predict, y_true) which outputs score metric
    folds (list): output of kfold_split
    knn_class (obj): class of knn model to fit

    Returns:
    dict: key - tuple of (normalizer_name, n_neighbors, metric, weight), value - mean score over all folds
    """
    ret = dict()
    for i in folds:
        for normalizers in parameters['normalizers']:
            x_train, x_test = x[i[0]], x[i[1]]
            if normalizers[0] is not None:
                normalizers[0].fit(x_train)
                x_train, x_test = normalizers[0].transform(x_train), normalizers[0].transform(x_test)
            for n_neighbors in parameters['n_neighbors']:
                for metrics in parameters['metrics']:
                    for weights in parameters['weights']:
                        clf = knn_class(n_neighbors=n_neighbors, weights=weights, metric=metrics)
                        clf.fit(x_train, y[i[0]])
                        score = score_function(y[i[1]], clf.predict(x_test))
                        if (normalizers[1], n_neighbors, metrics, weights) in ret:
                            ret[(normalizers[1], n_neighbors, metrics, weights)] += score / len(folds)
                        else:
                            ret[(normalizers[1], n_neighbors, metrics, weights)] = score / len(folds)
    return ret
