
from src.rocketparts.motorparts.oxtank import OxTank
from lib.simulation import Simulation
from lib.general import constant
from src.environment import Environment
from src.simulation.fill.logger import FillLogger


class FillSimulation(Simulation):
    def __init__(self, **kwargs):
        """
        fill_tank is the tank being emptied.
        run_tank is the tank being filled.
        flow_rate is the function to determine the flow rate out of the fill_tank. The entire FillSimulation object is passed to it. It should return a value in kg/s.
        head_loss is the function that calculates the pressure loss from fill_tank to run_tank. It should return a value in bar.
        
        """
        super().__init__(**kwargs)

        self.fill_tank = OxTank(ox_mass = 20)
        self.run_tank = OxTank(ox_mass = 0)
        self.head_loss = constant(5e5) # 5 bar
        self.flow_rate = constant(1)
        self.environment = Environment()
        self.logger = FillLogger(self)

        # Below this value, the tank stops draining.
        self.flow_rate_threshold = 0.1

        self.overwrite_defaults(**kwargs)
        self.override_subobjects()

    def simulate_step(self):
        mass_change = self.flow_rate(self) * self.time_increment
        self.fill_tank.update_drain(mass_change)
        self.run_tank.update_drain(-mass_change)

        self.save_previous()

        return super().simulate_step()

    def is_finished(self):
        """
        Return true if the rocket hasn't landed, false if it has.
        Used in run_simulation
        """
        if (self.fill_tank.ox_mass <= 0):
            print("Stopping for ox mass")
        
        if self.flow_rate(self) <= self.flow_rate_threshold:
            print("Stopping for flow rate")

        return self.fill_tank.ox_mass <= 0 or self.flow_rate(self) <= self.flow_rate_threshold

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, e):
        self._environment = e

        self.override_subobjects()

    def save_previous(self):
        self.p_flow_rate = self.flow_rate(self)

    def copy(self):
        new_environment = self.environment.copy()

        if self.logger is not None:
            new_logger = self.logger.copy()
        else:
            new_logger=None

        return FillSimulation(logger=new_logger, environment=new_environment)