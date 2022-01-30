
from logging import Logger


class CustomLogger(Logger):
    def __init__(self, logging_object, **kwargs):
        super().__init__(logging_object)

        self.partial_debugging = True
        self.debug_every = 10 # seconds
        self.last_debugged = 0

        self.overwrite_defaults(**kwargs)

        self.print_debug("Logger is prepared to run simulation")

    def display_partial_data(self):
        self.print(f"We are {self.simulation.environment.time} seconds through the simulation")
        self.last_debugged += self.debug_every

    def handle_frame(self):

        if self.partial_debugging and self.simulation.environment.time > self.last_debugged + self.debug_every:
            self.display_partial_data()


        return super().handle_frame()

            

