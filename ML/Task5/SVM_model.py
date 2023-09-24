import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV

class MinMaxScaler:
    def __init__(self):
        self.min = 0
        self.max = 0

    def fit(self, data):
        self.min, self.max = np.amin(data, axis=0), np.amax(data, axis=0)

    def transform(self, data):
        return np.array((data - self.min) / (self.max - self.min))


class StandardScaler:
    def __init__(self):
        self.expected = 0
        self.dispersion = 0

    def fit(self, data):
        self.expected = np.sum(data, axis=0) / data.shape[0]
        self.dispersion = np.std(data, axis=0)

    def transform(self, data):
        return np.array((data - self.expected) / self.dispersion)


def kfold_split(num_objects, num_folds):
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


def svc_cv_score(x, y, parameters, score_function, folds, svc_class):
    count = 1
    ret = dict()
    for i in folds:
        print(f'Fold: {count}/3...')
        count += 1
        for normalizers in parameters['normalizers']:
            print(f'\tNormalizer: {normalizers}')
            x_train, x_test = x.values[i[0]], x.values[i[1]]
            if normalizers[0] is not None:
                normalizers[0].fit(x_train)
                x_train, x_test = normalizers[0].transform(x_train), normalizers[0].transform(x_test)
            for C in parameters['C']:
                print(f'\t\tC: {C}')
                for kernel in parameters['kernels']:
                    print(f'\t\t\tkernel: {kernel}', end=', ')
                    if kernel == 'poly':
                        for power in parameters['degree']:
                            clf = svc_class(C=C, kernel=kernel, degree=power, class_weight='balanced')
                            clf.fit(x_train, y.values.ravel()[i[0]])
                            score = score_function(y.values[i[1]], clf.predict(x_test))
                            if (normalizers[1], C, kernel, power) in ret:
                                ret[(normalizers[1], C, kernel, power)] += score / len(folds)
                            else:
                                ret[(normalizers[1], C, kernel, power)] = score / len(folds)
                    else:
                        clf = svc_class(C=C, kernel=kernel, class_weight='balanced')
                        clf.fit(x_train, y.values.ravel()[i[0]])
                        score = score_function(y.values[i[1]], clf.predict(x_test))
                        if (normalizers[1], C, kernel) in ret:
                            ret[(normalizers[1], C, kernel)] += score / len(folds)
                        else:
                            ret[(normalizers[1], C, kernel)] = score / len(folds)
                print()
            print()
    return ret


if __name__ == "__main__":
    X_train, y_train = pd.read_csv('train_features.csv'), pd.read_csv('train_target.csv')
    X_test, y_test = pd.read_csv('test_features.csv'), pd.read_csv('test_target.csv')

    parameters = {
        'C': np.arange(1, 310) / 100,
        'kernels': ['linear', 'rbf'],
        'degree': [3, 4, 5],
        'normalizers': [(None, 'None')]  # , (MinMaxScaler(), 'MinMax'), (StandardScaler(), 'Standard')]
    }

    # results = svc_cv_score(X_train, y_train, parameters, accuracy_score, kfold_split(X_train.shape[0], 3), SVC)
    # print(max(results, key=results.get))  # ('Standard', 0.8, 'rbf')

    model = SVC(C=0.8, kernel='rbf', class_weight='balanced')
    model.fit(X_train, y_train)

    print('Train: ', accuracy_score(y_train, model.predict(X_train)))
    print('Test: ', accuracy_score(y_test, model.predict(X_test)))

