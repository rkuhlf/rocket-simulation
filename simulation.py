from preset_object import PresetObject


class Simulation(PresetObject):
    def __init__(self, config, environment, rocket, logger):
        self.environment = environment
        self.rocket = rocket
        self.logger = logger

        # It just isnt workin atm
        self.apply_angular_forces = False
        self.max_frames = -1
        self.frames = 0

        super().overwrite_defaults(config)

        rocket.apply_angular_forces = self.apply_angular_forces


        if self.rocket.logger is not logger:
            self.rocket.logger = logger

    def simulate_step(self):
        self.rocket.simulate_step()
        self.environment.simulate_step()
        # Also saves the row
        self.logger.handle_frame()

        self.frames += 1

    def end(self):
        self.logger.save_to_csv()

    def run_simulation(self):

        while not self.rocket.landed and (
                self.max_frames == -1 or self.max_frames > self.frames):
            self.simulate_step()

        self.end()
