import numpy as np


def evaluate_measures(sample):
    """Calculate measure of split quality (each node separately).

    Parameters
    ----------
    sample : a list of integers. The size of the sample equals to the number of objects in the current node. The integer
    values are equal to the class labels of the objects in the node.

    Returns
    -------
    measures - a dictionary which contains three values of the split quality.
    Example of output:

    {
        'gini': 0.1,
        'entropy': 1.0,
        'error': 0.6
    }
    """
    sample = np.array(sample)
    measures = {'gini': 0, 'entropy': 0, 'error': 0}

    _, counts = np.unique(sample, return_counts=True)
    freq = counts / sum(counts)

    measures['gini'] = sum(freq * (np.ones(len(freq)) - freq))
    measures['entropy'] = -sum(freq * np.log(freq))
    measures['error'] = 1 - max(freq)

    return measures


if __name__ == '__main__':
    print(evaluate_measures([1, 2, 3, 2, 3, 1, 2, 0]))
