import sys
sys.path.append(".")

from preset_object import PresetObject

# Finds the dynamic O/F stuff
# Keeps track of the change in chamber pressure
# The combustion chamber keeps track of the fuel grain and combustion
# The motor class connects ox tank to the injector to the combustion chamber to the nozzle

def find_characteristic_velocity_from_OF(ratio):
    # This part of the model should be completely empirical
    pass


def find_combustion_chamber_pressure():
    pass


class CombustionChamber(PresetObject):

    def __init__(self, config={}, fuel_grain=None):
        self.fuel_grain = fuel_grain

        # The inside of the engine starts off at atmospheric conditions
        self.initial_pressure = 101300 # Pa
        self.temperature = 273.15 + 23 # Kelvin

        super().overwrite_defaults(config)

        #region CALCULATED
        

        #endregion




    def get_change_in_pressure(self, ox_mass_flow):
        '''
        Returns the rate of pressure change with respect to time. 
        Based off of mass continuity in the combustion chamber.
        I believe this equation is absolutely correct
        '''
        # d(P_c)/d(t) = [m-dot_ox + (rho_f - rho_c)*A_b*a*G_ox^n - P_c*A_t/c*_exp] * R*T_C / V_C
