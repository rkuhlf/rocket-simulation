# FIN CLASSES
# Fins are basically just a mass object with a few additional evaluation methods.
# Since all of the drag data on the rocket is determined by a CD lookup, it is not necessary to include a fin object, but I want one anyways just for some fin flutter stuff


# TODO: finish implementing this class


import sys
sys.path.append(".")

from RocketParts.massObject import MassObject

class Fins(MassObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # CR	=	fin root chord
        self.CR =
        # CT	=	fin tip chord
        self.CT =
        # S	=	fin semispan
        self.S =
        # LF	=	length of fin mid-chord line
        self.LF =
        # XR	=	distance between fin root leading edge and fin tip leading edge parallel to body
        self.XR =
        # N	=	number of fins
        self.N = 3

        super().overwrite_defaults(**kwargs)

# Elliptical fin class
