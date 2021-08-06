from nose import OgiveNose


class RocketFrame(PresetObject):
    '''Stores information for calculating the CP'''

    def __init__(self, config={}):
        # Meters from the nose tip
        self.center_of_pressure = 10

        super().overwrite_defaults(config)

    def get_CP(self):
        return self.center_of_pressure


class LookupBasicFrame(RocketFrame):
    # Doesn't include the effects of differing angles. This one should be used for 1D simulations
    # We always need to include the mach, otherwise there isn't any point to having a table

    def __init__(self, config={}):
        # Meters from the nose tip
        self.center_of_pressure = 10

        super().overwrite_defaults(config)

    def get_CP(self, mach):
        pass


class LookupFrame(LookupBasicFrame):
    def __init__(self, config={}):
        # Meters from the nose tip
        self.center_of_pressure = 10

        super().overwrite_defaults(config)

    def get_CP(self, angle_of_attack, mach):
        pass


# basically just requires fins, nose, and boattail classes
# Takes a bool argument, distinct centers of pressure, in which case it will return a dictionary
class CalculatedFrame(RocketFrame):
    def __init__(self, config={}):
        pass
        # # All of thise stuff should be overridden, these are just reasonable defaults
        # # LN	=	length of nose
        # self.nose = OgiveNose()
        # # d	=	diameter at base of nose
        # self.d = 0.5
        # # dF	=	diameter at front of transition
        # self.dF = 0.5
        # # dR	=	diameter at rear of transition
        # self.dR = 0.4
        # # LT	=	length of transition
        # self.LT = 2
        # # XP	=	distance from tip of nose to front of transition
        # self.XP = 3

        # # R	=	radius of body at aft end
        # self.R =

        # # XB	=	distance from nose tip to fin root chord leading edge
        # self.XB =




        # super().overwrite_defaults(config)


    def get_CP(self, angle_of_attack, mach):
        pass
