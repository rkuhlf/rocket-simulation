class Fins(PresetObject):
    def __init__(self, config={}):
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

        super().overwrite_defaults(config)

# Elliptical fin class
