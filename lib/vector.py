import numpy as np

class Vector(np.ndarray):
    def __new__(cls, x, y, z):
        obj = np.asarray([x, y, z], dtype="float64").view(cls)
        return obj
    
    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]
    
    @property
    def z(self):
        return self[2]