import pytest
import numpy as np
from distance_matrix.distance_matrix import build_distance_matrix_manhattan

query = [
    (-34.5781371164943, -58.42682272642635),
    (-34.5761481253388, -58.448498667294096),
    (-34.59474602196079, -58.444581328583055),
    (-34.611459076272595, -58.42114258525853),
    (-34.592693148131325, -58.37555238425974),
    ]
expected = np.array([
    [   0, 2228, 3507, 4267, 6375],
    [2228,    0, 2451, 6495, 8603],
    [3507, 2451,    0, 4044, 6612],
    [4267, 6495, 4044,    0, 6322],
    [6375, 8603, 6612, 6322,    0]
])

def test_distance_matrix_manhattan_correct_shape_and_type():
    matriz = build_distance_matrix_manhattan(query)
    
    assert isinstance(matriz, np.ndarray)
    assert matriz.dtype == np.int32
    assert matriz.shape == (len(query), len(query))
    assert np.all(np.diag(matriz) == 0)


def test_manhattan_is_symmetric():
    matriz = build_distance_matrix_manhattan(query)
    assert np.array_equal(matriz, matriz.T)

def test_manhattan_values():

    matrix_manhattan = build_distance_matrix_manhattan(query, multiplier=1.01)

    assert np.array_equal(matrix_manhattan, expected)