

from abc import ABC
import string
from typing import Callable
import numpy as np

import pandas as pd
from lib.decorators import diametered
from lib.data import interpolated_lookup, interpolated_lookup_2D
from lib.presetObject import PresetObject

# For now, I am assuming that all grains have a constant OD

@diametered("outer_radius", "outer_diameter")
class GrainGeometry(PresetObject, ABC):
    """Should not contain any information about the fuel itself. So no properties like density or viscosity."""
    

    def __init__(self, **kwargs) -> None:
        """For the moment, you have to manually set the initial port volume and the fuel volume"""

        self.outer_radius = 0.25
        self.length = 0.4 # m

        
        # These values will be calculated
        self._fuel_volume = self.total_volume
        self._port_volume = None
        self.port_area = None
        self.burn_area = None

        self.length_regressed = 0

        self._area_function: Callable = None

        self.overwrite_defaults(**kwargs)

        self.calculate_area()
    
    @property
    def port_volume(self) -> float:
        return self._port_volume
    
    @port_volume.setter
    def port_volume(self, v):
        self._port_volume = v
        self._fuel_volume = self.total_volume - v
        self.calculate_area()
    
    @property
    def fuel_volume(self):
        return self._fuel_volume
    
    @fuel_volume.setter
    def fuel_volume(self, v):
        self._fuel_volume = v
        self._port_volume = self.total_volume - v
        self.calculate_area()
    

    @property
    def area_function(self):
        return self._area_function
    
    @area_function.setter
    def area_function(self, a):
        self._area_function = a
        self.calculate_area()
    
    
    def calculate_area(self):
        if self.area_function is None:
            return 0, 0, 0
        
        self.burn_area, self.port_area, self._port_volume = self.area_function(self)
        self._fuel_volume = self.total_volume - self.port_volume

    def update_regression(self, regression_amount: float):
        self.length_regressed += regression_amount

        volume_change = regression_amount * self.burn_area
        self.fuel_volume -= volume_change

        return volume_change

    @property
    def effective_radius(self):
        """The radius that gives the same port area as a circle port."""
        return np.sqrt(self.port_area / np.pi)
    
    @property
    def total_volume(self):
        return np.pi * self.outer_radius ** 2 * self.length
    

    @property
    def burned_through(self):
        return self.port_volume > self.total_volume




#region Burn Area Equations/Algorithms/Lookups
# Ideally, all of these would work for any grain, but there are probably specialized algorithms, so we will just roll with it.
# Since the burn area and the cross sectional area are inherently coupled, these functions return both those things
def get_areas_csv(table_path: string, per_meter: bool = True):
    """Create a function to lookup the burn area from the port volume. If per_meter is true, it will be multiplied by the length of the grain."""
    # I do not know if passing this variable like this will work how I want
    df = pd.read_csv(table_path)

    
    def burn_area_func(grain: GrainGeometry):
        # TODO: write port volume function; adds regression * burn_area every time
        r = grain.length_regressed
        
        burn_area = interpolated_lookup(df, "LengthRegressed", r, "BurnArea", safe=True)
        port_area = interpolated_lookup(df, "LengthRegressed", r, "PortArea", safe=True)
        port_volume = interpolated_lookup(df, "LengthRegressed", r, "PortVolume", safe=True)

        if per_meter:
            burn_area *= grain.length
            port_volume *= grain.length
        
        return burn_area, port_area, port_volume

    return burn_area_func

def get_areas_cylindrical(grain: "Annular"):
    burn_area = np.pi * grain.port_radius * 2 * grain.length
    port_area = np.pi * grain.port_radius ** 2
    port_volume = port_area * grain.length

    return burn_area, port_area, port_volume

def multiply_areas(original_func: Callable, burn_area_multiplier=1, port_area_multiplier=1, port_volume_multiplier=1):
    # Unfortunatel coupled to the return signature of burn area func
    def new_func(*args, **kwargs):
        burn_area, port_area, port_volume = original_func(*args, **kwargs)

        return burn_area_multiplier * burn_area, port_area_multiplier * port_area, port_volume_multiplier * port_volume
    
    return new_func


#endregion


@diametered("port_radius", "port_diameter")
class Annular(GrainGeometry):
    def __init__(self, **kwargs) -> None:
        """Accepts a port_radius or port_diameter, as well as the outer_diameter"""
        super().__init__(**kwargs)

        self._port_radius = 0.05 # m
        self.area_function = get_areas_cylindrical

        self.overwrite_defaults(**kwargs)

    # @property for radius to update stuff when it gets set
    @property
    def port_radius(self):
        return self._port_radius
    
    @port_radius.setter
    def port_radius(self, r):
        self._port_radius = r
        self.calculate_area()
    
    def update_regression(self, regression_amount: float):
        self.port_radius += regression_amount
        return super().update_regression(regression_amount)



class StarSwirl(GrainGeometry):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.area_function = get_areas_csv("Data/Input/Regression/regressionLookup.csv")

        self.overwrite_defaults(**kwargs)
    
    



if __name__ == "__main__":
    g = GrainGeometry()
    g.effective_radius