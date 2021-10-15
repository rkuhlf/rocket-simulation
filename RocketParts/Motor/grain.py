import numpy as np
import sys
sys.path.append(".")

from preset_object import PresetObject


class Grain(PresetObject):
    def __init__(self, config={}):
        self.inner_radius = 0.05 # random
        self.outer_radius = 0.1016 # random
        # of the fuel
        self.mass_flow = 0
        self.density = 920 # kg / m^3
        self.length = 1.4 # m

        super().overwrite_defaults(config)

    def get_outer_cross_sectional_area(self):
        return np.pi * self.outer_radius ** 2


    def get_regression_rate(self, mass_flux):
        # This is the famous regression rate equation that is so hard to get right. I think this is an equation for Paraffin-Nitrous
        leading_ballistic_coefficient = 1.550 * 10 ** -4
        exponential_ballistic_coefficient = 0.5
        return leading_ballistic_coefficient * mass_flux ** exponential_ballistic_coefficient

    def get_volume_flow(self):
        return self.mass_flow / self.density

    def update_regression(self, ox_flow, time_increment):
        port_area = np.pi * self.inner_radius ** 2
        ox_flux = ox_flow / port_area
        # Give a warning if ox flux is too big: might blow fire out, might cause combustion instability
        if ox_flux > 700: # assumes kg/m^2
            raise Warning("McLeod told us not to go past 500 kg/m^2-s. He warned of blowing the flame out, but I have also seen some combustion instability stuff.")

        if self.inner_radius > self.outer_radius:
            raise Warning("You have burned through the entire fuel grain")
            return

        # Right now this is space-averaged. TODO: It might be kind of fun to do a not space-averaged thing, just simulating about 25 separate points along the grain
        burn_area = 2 * np.pi * self.inner_radius * self.length
        regression_rate = self.get_regression_rate(ox_flux)
        self.mass_flow = regression_rate * burn_area * self.density

        regressed_distance = regression_rate * time_increment
        self.inner_radius += regressed_distance


        