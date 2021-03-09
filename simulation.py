
class Simulation:
    def __init__(self, environment, rocket, logger):
        self.environment = environment
        self.rocket = rocket
        self.logger = logger

        if self.rocket.logger is not logger:
            self.rocket.logger = logger

    def simulate_step(self):
        self.rocket.simulate_step()
        self.environment.simulate_step()
        # Also saves the row
        self.logger.handle_frame()

    def end(self):
        self.logger.save_to_csv()

    def run_simulation(self):

        while not self.rocket.landed:
            self.simulate_step()

        self.end()
