from preset_object import PresetObject


class Simulation(PresetObject):
    def override_subobjects(self):
        self.rocket.apply_angular_forces = self.apply_angular_forces

        if self.rocket.logger is not self.logger:
            self.rocket.logger = self.logger

        if self.rocket.environment is not self.environment:
            self.rocket.environment = self.environment

    def __init__(self, config, environment, rocket, logger=None):
        self.environment = environment
        self.rocket = rocket
        self.logger = logger

        self.apply_angular_forces = True
        self.max_frames = -1
        self.frames = 0
        self.stopping_errors = True

        super().overwrite_defaults(config)

        self.override_subobjects()

    def reset(self):
        super().reset()

        # This is very necessary and it kind of makes resetting the other stuff pointless
        self.override_subobjects()

    def simulate_step(self):
        self.rocket.simulate_step()
        self.environment.simulate_step()
        if self.logger is not None:
            # Also saves the row
            self.logger.handle_frame()

        self.frames += 1


    def end(self):
        if self.logger is not None:
            self.logger.save_to_csv()

    def run_simulation(self):
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

        self.end()
