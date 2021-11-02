# SIMULATION CLASS
# This is the file for the basic connections between a rocket, a logger, and an environment
# It doesn't really do much math, but there are a few basic utilities that help in other places

from presetObject import PresetObject

from Helpers.general import magnitude
from logger import Logger

# For defaults
from environment import Environment

class Simulation(PresetObject):
    """
    Provide a base class for all frame-by-frame iterative simulations
    They always provide integration with a logger
    I don't really expect anyone to instantiate this class, you should use RocketSimulation or MotorSimulation.
    """

    def override_subobjects(self):
        """
        Ensure that all of the subobjects the simulation references have the correct memory addresses in there
        This should almost always be overriden
        """
        if self.logger is not None:
            self.logger.simulation = self

    def __init__(self, **kwargs):
        """
        You could potentially pass in a logger, but a default one will be created for you
        Other variables are max_frames and stopping_errors
        """
        # FIXME: this one is not going to work with keyword arguments
        self._logger = Logger(self)
        self.max_frames = -1
        self.frames = 0
        self.stop_on_error = True

        super().overwrite_defaults(**kwargs)

        self.override_subobjects()

    def reset(self):
        super().reset()

        # This is very necessary and it kind of makes resetting the other stuff pointless
        self.override_subobjects()

    def copy(self):
        # FIXME: I think I designed it like this to work with one of the genetic simulations, I need to make it better so that I can use it with a config
        return Simulation(logger=self.logger)


    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, l):
        self._logger = l

        self.override_subobjects()


    def simulate_step(self):
        if self.logger is not None:
            # Also saves the row
            self.logger.handle_frame()

        self.frames += 1

    def end(self):
        if self.logger is not None:
            self.logger.save_to_csv()

    @property
    def should_continue_simulating(self):
        """This should be overridden, otherwise it will always go to the max frames"""
        return True

    @property
    def frames_remaining(self):
        """Return a boolean that is false if we have reached the maximum number of frames, given that the max isn't -1"""
        return self.max_frames == -1 or self.max_frames > self.frames
    

    def run_simulation(self):
        try:
            if self.stop_on_error:
                while self.should_continue_simulating and self.frames_remaining:
                    self.simulate_step()
            else:
                try:
                    while self.should_continue_simulating and self.frames_remaining:
                        self.simulate_step()
                except (Exception) as e:
                    print(e)
                
        finally:
            self.end()




class RocketSimulation(Simulation):
    """
    A class designed to piece together the components of a frame-by-frame rocket simulation
    """

    def override_subobjects(self):
        super().override_subobjects()

        # This might be called by the environment setter before we have established the rocket
        if self.rocket is not None:
            self.rocket.apply_angular_forces = self.apply_angular_forces

            if self.rocket.logger is not self.logger:
                self.rocket.logger = self.logger

            if self.rocket.environment is not self.environment:
                self.rocket.environment = self.environment

    def __init__(self, **kwargs):
        self._environment = Environment()
        self.rocket = None

        self.apply_angular_forces = True

        # This should already override the defaults in here, but I have an additional one because it wasn't working
        super().__init__(**kwargs)
        # super().overwrite_defaults(**kwargs)

        self.rail_gees = None
        self.rail_velocity = None

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, e):
        self._environment = e

        self.override_subobjects()

    def copy(self):
        # Often when doing genetic sims, it is important to make a copy of the object

        new_environment = self.environment.copy()
        new_rocket = self.rocket.copy()

        if self.logger is not None:
            new_logger = self.logger.copy()
            new_logger.rocket = new_rocket
        else:
            new_logger=None

        return RocketSimulation(environment=new_environment, rocket=new_rocket, logger=new_logger)


    def simulate_step(self):
        self.rocket.simulate_step()
        self.environment.simulate_step()
        if self.logger is not None:
            # Also saves the row
            self.logger.handle_frame()
        
        # TODO: check that this rail_gees is good based on the output.csv file. Right now it seems a teeny bit high
        if self.environment.rail_length < self.rocket.position[2] and self.rail_gees is None:
            self.rail_gees = self.rocket.gees
            self.rail_velocity = magnitude(self.rocket.velocity)

        self.frames += 1

    @property
    def should_continue_simulating(self):
        """
        Return true if the rocket hasn't landed, false if it has.
        Used in run_simulation
        """
        return not self.rocket.landed


    #region Helpers to evaluate the flight

    @property
    def dist_from_start(self):
        return (self.rocket.position[0] ** 2 + self.rocket.position[1] ** 2) ** (1 / 2)

    @property
    def landing_speed(self):
        # Hopefully the rocket is frozen in its last frame
        return self.rocket.velocity[2]


    # The property means that it re-looks it up every time, so it is automatically updated when the rocket changes
    @property
    def apogee(self):
        return self.rocket.apogee

    @property
    def max_velocity(self):
        return self.rocket.max_velocity
    
    @property
    def max_mach(self):
        return self.rocket.max_mach

    @property
    def max_net_force(self):
        return self.rocket.max_net_force

    # endregion


class MotorSimulation(Simulation):
    """
    A class designed to piece together the components of a frame-by-frame custom motor simulation.
    It will not work with a pre-designed thrust curve, but I don't know why you would bother simulating that
    Only the motor argument is required, but it should already contain references to the other objects (ox tank, injector, chamber, and nozzle)
    """

    def override_subobjects(self):
        if self.motor is not None:
            if self.motor.logger is not self.logger:
                self.motor.logger = self.logger

            if self.motor.environment is not self.environment:
                self.motor.environment = self.environment

            self.grain.stop_on_error = self.stop

    def __init__(self, **kwargs):
        self._environment = Environment()
        self.motor = None

        super().__init__(**kwargs)

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, e):
        self._environment = e

        self.override_subobjects()

    def copy(self):
        new_environment = self.environment.copy()
        new_motor = self.motor.copy()

        if self.logger is not None:
            new_logger = self.logger.copy()
            new_logger.motor = new_motor
        else:
            new_logger=None

        return MotorSimulation(environment=new_environment, motor=new_motor, logger=new_logger)


    def simulate_step(self):
        super().simulate_step()

    @property
    def should_continue_simulating(self):
        return self.tank.pressure < self.chamber.pressure or self.tank.ox_mass <= 0 or self.grain.inn
        
    #region Shortcuts for easier access
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
    def grain(self):
        return self.motor.combustion_chamber.fuel_grain

    @property
    def nozzle(self):
        return self.nozzle

    #endregion

    #region Helpers to evaluate the burn

    # endregion
