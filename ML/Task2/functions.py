from typing import List


def prod_non_zero_diag(X: List[List[int]]) -> int:
    """
    Compute product of nonzero elements from matrix diagonal, 
    return -1 if there is no such elements. ([[1, 0, 1], [2, 0, 2], [3, 0, 3], [4, 4, 4]])
    Return type: int
    """
    prod = 0
    for i in range(len(X[0])):
        if X[i][i] == 0:
            continue
        if prod == 0:
            prod = X[i][i]
        else:
            prod *= X[i][i]
    return -1 if prod == 0 else prod


def are_multisets_equal(x: List[int], y: List[int]) -> bool:
    """
    Return True if both 1-d arrays create equal multisets, False if not.
    Return type: bool
    """
    return sorted(x) == sorted(y)


def max_after_zero(x: List[int]) -> int:
    """
    Find max element after zero in 1-d array, 
    return -1 if there is no such elements.
    Return type: int
    """
    ret = int()
    is_def = False
    for i in range(0, len(x) - 1):
        if x[i] == 0:
            if is_def:
                if x[i + 1] > ret:
                    ret = x[i + 1]
            else:
                ret = x[i + 1]
                is_def = True
    return ret if is_def else -1


def convert_image(image: List[List[List[float]]], weights: List[float]) -> List[List[float]]:
    """
    Sum up image channels with weights.
    Return type: List[List[float]]
    """
    ret = []
    for x in range(len(image)):
        ret.append([])
        for y in range(len(image[0])):
            sum = 0.0
            ret[x].append([])
            for w in range(len(weights)):
                sum += image[x][y][w] * weights[w]
            ret[x][y] = sum
    return ret


def run_length_encoding(x: List[int]) -> (List[int], List[int]):
    """
    Make run-length encoding.
    Return type: (List[int], List[int])
    """

    def ret(lst, i=0):
        while lst[i] == lst[0]:
            i += 1
            if i == len(lst):
                break
        return lst[0], i

    code, length, index, i = [], [], 0, 0
    while i != len(x):
        num, size = ret(x[i:])
        code.append(num)
        length.append(size)
        i += length[index]
        index += 1
    return code, length


def pairwise_distance(X: List[List[float]], Y: List[List[float]]) -> List[List[float]]:
    """
    Return pairwise object distance.
    Return type: List[List[float]]
    """

    def dist(x, y):
        euclid = 0
        for i in range(len(x)):
            euclid += (x[i] - y[i]) ** 2
        return euclid ** 0.5

    ret = []
    for i in range(len(X)):
        ret.append([])
        for j in range(len(Y)):
            ret[i].append(dist(X[i], Y[j]))
    return ret


if __name__ == "__main__":
    print(prod_non_zero_diag([[1, 0, 1], [2, 0, 2], [3, 0, 3], [4, 4, 4]]))
    print(are_multisets_equal([1], [1, 2]))
    print(max_after_zero([6, 2, 0, 3, 0, 0, 5, 7, 0]))
    print(run_length_encoding([0]))
    print(pairwise_distance([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[9, 8, 7], [6, 5, 4], [3, 2, 1]]))
