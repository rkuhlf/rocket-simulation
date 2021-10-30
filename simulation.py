# SIMULATION CLASS
# This is the file for the basic connections between a rocket, a logger, and an environment
# It doesn't really do much math, but there are a few basic utilities that help in other places

from preset_object import PresetObject

from Helpers.general import magnitude


class Simulation(PresetObject):
    def override_subobjects(self):
        self.rocket.apply_angular_forces = self.apply_angular_forces

        if self.rocket.logger is not self.logger:
            self.rocket.logger = self.logger

        if self.rocket.environment is not self.environment:
            self.rocket.environment = self.environment

    def __init__(self, config={}, environment=None, rocket=None, logger=None):
        self.environment = environment
        self.rocket = rocket
        self.logger = logger

        self.apply_angular_forces = True
        self.max_frames = -1
        self.frames = 0
        self.stopping_errors = True

        super().overwrite_defaults(config)

        self.override_subobjects()

        self.rail_gees = None
        self.rail_velocity = None

    def reset(self):
        super().reset()

        # This is very necessary and it kind of makes resetting the other stuff pointless
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

        return Simulation({}, environment=new_environment, rocket=new_rocket, logger=new_logger)

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


    def end(self):
        if self.logger is not None:
            self.logger.save_to_csv()

    def run_simulation(self):
        try:
            if self.stopping_errors:
                try:
                    while not self.rocket.landed and (
                            self.max_frames == -1 or self.max_frames > self.frames):
                        self.simulate_step()
                except (Exception) as e:
                    print(e)
                    # print(e.with_traceback())

            else:
                while not self.rocket.landed and (
                        self.max_frames == -1 or self.max_frames > self.frames):
                    self.simulate_step()
        finally:
            self.end()


    # region Helpers to evaluate the flight

    @property
    def max_velocity(self):
        pass
    
    @property
    def max_mach(self):
        pass

    @property
    def dist_from_start(self):
        return (self.rocket.position[0] ** 2 + self.rocket.position[1] ** 2) ** (1 / 2)

    @property
    def landing_speed(self):
        return self.rocket.velocity[2]

    @property
    def apogee(self):
        return self.rocket.apogee

    # endregion
