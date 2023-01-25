from lib.simulation import Simulation
from src.simulation.rocket.logger import RocketLogger
from src.environment import Environment
from lib.general import magnitude

class RocketSimulation(Simulation):
    """
    A class designed to piece together the components of a frame-by-frame rocket simulation
    """

    def override_subobjects(self):
        # Super deals with logger.
        super().override_subobjects()
        
        if self.environment is not None:
            self.environment.simulation = self

        # This might be called by the environment setter before we have established the rocket
        if self.rocket is not None:
            self.rocket.apply_angular_forces = self.apply_angular_forces
            self.rocket.simulation = self

            # The simulation logger wins out over the rocket logger.
            if self.rocket.logger is not self.logger:
                self.rocket.logger = self.logger
            
            if self.rocket.simulation is not self:
                self.rocket.simulation = self

            if self.rocket.environment is not self.environment:
                self.rocket.environment = self.environment


    def __init__(self, **kwargs):
        # This will also override defaults, but we really just need to get the super stuff set up.
        super().__init__(**kwargs)

        self._environment = Environment()
        self.rocket: Rocket = None

        self.apply_angular_forces = True
        self.logger = RocketLogger(self)

        # Now we override defaults to get rid of anything we don't want.
        self.overwrite_defaults(**kwargs)
        self.override_subobjects()

        self.rail_gees = None
        self.rail_velocity = None

    @property
    def environment(self):
        try:
            return self._environment
        except AttributeError:
            return None

    @environment.setter
    def environment(self, e):
        self._environment = e

        self.override_subobjects()

    @property
    def rocket(self):
        try:
            return self._rocket
        except AttributeError:
            return None

    @rocket.setter
    def rocket(self, r):
        self._rocket = r

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

        if self.environment.rail_length < self.rocket.position[2] and self.rail_gees is None:
            self.rail_gees = self.rocket.gees
            self.rail_velocity = magnitude(self.rocket.velocity)
        
        super().simulate_step()

    def is_finished(self):
        """
        Return true if the rocket hasn't landed, false if it has.
        Used in run_simulation
        """
        return self.rocket.landed


    #region helpers to evaluate the flight

    @property
    def dist_from_start(self) -> float:
        return (self.rocket.position[0] ** 2 + self.rocket.position[1] ** 2) ** (1 / 2)

    @property
    def landing_speed(self):
        if not self.rocket.landed:
            raise Exception("Rocket has not yet landed.")

        # Hopefully the rocket is frozen in its last frame
        return self.rocket.velocity[2]


    # The property means that it re-looks it up every time, so it is automatically updated when the rocket changes
    @property
    def apogee(self):
        return self.rocket.apogee

    @property
    def apogee_lateral_velocity(self):
        return self.rocket.apogee_lateral_velocity
    
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

class RocketSimulationToApogee(RocketSimulation):
    @property
    def is_finished(self):
        # We only need to go until the apogee is set
        return self.apogee is not None
