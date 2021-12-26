import numpy as np


def _calcError(x_points, y_points, degree):
    if len(x_points) != len(y_points):
        return -1
    coefficients, *_ = np.polyfit(x_points, y_points, degree, full=True)
    chunk_models = np.poly1d(coefficients)
    fitted = chunk_models(x_points)
    error = (100 * y_points - 100 * fitted) ** 2
    return np.sum(error)


def _getOverlappedChunk(chunk_size, overlap, chunk_order):
    start, end = 0, chunk_size - 1
    if overlap > 1:
        overlap = overlap / 100
    step = int((1 - overlap) * chunk_size)
    shift = chunk_order * step
    return start + shift, end + shift


def getError(degree, num_of_chunks, overlap, x_data, y_data):
    if len(x_data) != len(y_data):
        return -1
    total_error = 0
    chunk_size = int(len(x_data) / num_of_chunks)
    for i in range(num_of_chunks):
        start, end = _getOverlappedChunk(chunk_size, overlap, i)
        if i == num_of_chunks - 1:
            end = len(x_data) - 1
        x_points = x_data[start: end]
        y_points = y_data[start: end]
        total_error += _calcError(x_points, y_points, degree)
    return total_error
