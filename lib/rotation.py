import numpy as np

class Rotation(np.ndarray):
    def __new__(cls, around, down):
        obj = np.asarray([around, down], dtype="float64").view(cls)
        return obj

    @property
    def around(self):
        return self[0]

    @property
    def down(self):
        return self[1]