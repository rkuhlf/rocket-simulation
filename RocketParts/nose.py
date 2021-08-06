# Since there are so many different kinds of nose cones, I figured I would try and make it as easy to expand on as possible. That means making a separate class

class Nose(presetObject):
    """Basically just an interface for all of the different types"""

    def __init__(self, config={}):
        # The only thing that I can think that might eventually want to go here is mass
        # maybe coefficient of drag

        # Actually a LN variable would be super useful. Then it could be calculated from the inputs of the other things, but it has to be there
        self.LN = 1  # m
        self.d = 0.5  # m

        super().overwrite_defaults(config)


class OgiveNose(Nose):
    """A nose cone formed by a circle's extension from the rest of the rocket's body"""

    def __init__(self, config={}):
        self.p = 4
        self.R = 2

        super().__init__(config=config)

        # There are lots of ways of defining an ogive nose. Maybe I should just accept any arguments and calculate the rest of the stuff
        o = self.p - self.R
        self.LN = (self.p ** 2 - o ** 2) ** (1 / 2)
        self.d = self.R * 2
