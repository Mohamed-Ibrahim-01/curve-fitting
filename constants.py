import numpy as np

NUMBER_OF_CHUNKS = "Number of Chunks"
POLYNOMIAL_DEGREE = "Polynomial Degree"
OVERLAP = "Overlap Percentage"
LABEL_PAIRS = {
    (OVERLAP, POLYNOMIAL_DEGREE),
    (NUMBER_OF_CHUNKS, POLYNOMIAL_DEGREE),
    (NUMBER_OF_CHUNKS, OVERLAP)
}
TICKS = [f'{tick}' if tick%5 == 0 else '' for tick in np.arange(1, 31)]
