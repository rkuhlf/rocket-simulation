# PRE and POST COMBUSTION
# TODO: This should probably just be an extension of the mass object as cylindrical mass object. I could even have the initializer take a parameter hollow, in which case it would just return a different object



from rocketparts.massObject import MassObject
from helpers.decorators import diametered
from helpers.general import cylindrical_volume


@diametered
class MixingChamber(MassObject):
    def __init__(self, **kwargs):
        self.length = 2
        self.radius = 4

        super().overwrite_defaults(**kwargs)

    @property
    def volume(self):
        return cylindrical_volume(self.length, self.radius)


class PrecombustionChamber(MixingChamber):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.radius = 0.1778
        self.length = self.radius

        super().overwrite_defaults(**kwargs)
        

class PostcombustionChamber(MixingChamber):
    """Basically just a different set of defaults for mixing chamber"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.radius = 0.1778
        self.length = self.diameter

        
        super().overwrite_defaults(**kwargs)

