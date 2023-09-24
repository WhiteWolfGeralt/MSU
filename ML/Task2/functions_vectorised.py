import numpy as np


def prod_non_zero_diag(X: np.ndarray) -> int:
    """
    Compute product of nonzero elements from matrix diagonal, 
    return -1 if there is no such elements.
    Return type: int / np.integer / np.int32 / np.int64
    """
    X = X.diagonal()
    if np.all(X == 0):  # все нули на диагонали
        return -1
    else:
        return int(np.prod(X[X != 0]))


def are_multisets_equal(x: np.ndarray, y: np.ndarray) -> bool:
    """
    Return True if both 1-d arrays create equal multisets, False if not.
    Return type: bool / np.bool_
    """
    return (np.sort(x) == np.sort(y)).all()


def max_after_zero(x: np.ndarray) -> int:
    """
    Find max element after zero in 1-d array, 
    return -1 if there is no such elements.
    Return type: int / np.integer / np.int32 / np.int64
    """
    mask = (x == 0)
    res = x[1:][mask[:-1]]
    return res.max() if res.size != 0 else -1


def convert_image(image: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Sum up image channels with weights.
    Return type: np.ndarray
    """


def run_length_encoding(x: np.ndarray) -> (np.ndarray, np.ndarray):
    """
    Make run-length encoding.
    Return type: (np.ndarray, np.ndarray)
    """
    mask = np.hstack((np.array(True), (x[:-1] != x[1:])))
    mask = np.arange(len(mask))[mask]
    return x[mask], np.append(mask[1:], x.size) - mask


def pairwise_distance(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """
    Return pairwise object distance.
    Return type: np.ndarray
    """
    sumx = np.sum(X ** 2, axis=1)
    sumy = np.sum(Y ** 2, axis=1)
    return np.sqrt(np.add.outer(sumx, sumy) - 2 * np.dot(X, Y.T))


if __name__ == "__main__":
    # print(prod_non_zero_diag(np.array([[1, 0, 1], [2, 0, 2], [3, 0, 3], [4, 4, 4]])))
    # print(are_multisets_equal(np.array([1]), np.array(([1, 2]))))
    # print(max_after_zero(np.array([6, 2, 0, 3, 0, 0, 5, 7, 0])))
    print(run_length_encoding(np.array(([2, 2, 2, 3, 3, 3, 5, 2]))))
    print(pairwise_distance(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]])))
