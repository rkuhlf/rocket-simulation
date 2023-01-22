from lib.simulation import Simulation
from src.simulation.motor.logger import MotorLogger
from src.environment import Environment


class MotorSimulation(Simulation):
    """
    Designed to piece together the components of a frame-by-frame custom motor simulation.
    It will not work with a pre-designed thrust curve
    Only the motor argument is required, but it should already contain references to the other objects (ox tank, injector, chamber, and nozzle)
    """

    def override_subobjects(self):
        super().override_subobjects()

        if self.motor is not None:
            if self.motor.logger is not self.logger:
                self.motor.logger = self.logger

            if self.motor.environment is not self.environment:
                self.motor.environment = self.environment

            self.grain.stop_on_error = self.stop_on_error

    def __init__(self, **kwargs):
        self._environment = Environment()
        self.motor: Motor = None

        super().__init__(**kwargs)

    def copy(self):
        new_environment = self.environment.copy()
        new_motor = self.motor.copy()

        if self.logger is not None:
            new_logger = self.logger.copy()
            new_logger.motor = new_motor
        else:
            new_logger=None

        return MotorSimulation(environment=new_environment, motor=new_motor, logger=new_logger)

    def initialize_simulation(self):
        self.motor.initialize_simulation()

    def simulate_step(self):
        thrust = self.motor.calculate_thrust()
        self.environment.simulate_step()
        
        super().simulate_step()

    @property
    def is_finished(self):
        return not (self.tank.pressure > self.chamber.pressure and self.tank.ox_mass > 0 and not self.grain.burned_through)
        
    def end(self):
        self.motor.end()

        return super().end()
    
    #region Shortcuts objects
    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, e):
        self._environment = e

        self.override_subobjects()


    @property
    def tank(self):
        return self.motor.ox_tank

    @property
    def injector(self):
        return self.motor.injector

    @property
    def chamber(self):
        return self.motor.combustion_chamber

    @property
    def grain(self) -> Grain:
        return self.motor.combustion_chamber.fuel_grain

    #endregion

    #region helpers to evaluate the burn

    @property
    def total_impulse(self):
        return self.motor.total_impulse

    @property
    def burn_time(self):
        return self.motor.burn_time

    @property
    def average_thrust(self):
        return self.total_impulse / self.burn_time

    @property
    def specific_impulse(self):
        """Return the overall specific impulse for the whole of the designed motor"""

        return self.total_specific_impulse

    @property
    def used_specific_impulse(self):
        return self.motor.used_specific_impulse

    @property
    def total_specific_impulse(self):
        return self.motor.total_specific_impulse

    # endregion
