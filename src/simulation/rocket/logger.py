from src.constants import output_path

from lib.logger import FeedbackLogger
from lib.general import magnitude
from src.simulation.rocket.logger_features import *

class RocketLogger(FeedbackLogger):
    """
        Logs the progress of the rocket simulation along with some print statements.
    """

    def __init__(self, simulation, **kwargs):
        # You need to make sure the parent's override doesn't override the self values we have already established, so we set our defaults after this
        super().__init__(simulation)

        # Don't want to override the ones added in super()
        self.features.union(base_features)


        self.debug_every = 20 # seconds
        self.full_path = f"{output_path}/output.csv"

        self.overwrite_defaults(**kwargs)

        self.printed_rail_stats = False
        self.printed_thrusted = False
        self.turned = False



    # Make it so that you can access it via either the logging_object or rocket property
    @property
    def rocket(self):
        return self.simulation.rocket

    @rocket.setter
    def rocket(self, r):
        self.simulation.rocket = r

    def display_partial_data(self):
        super().display_partial_data()

        if self.rocket.ascending:
            print(f"Rocket is ascending at {self.rocket.velocity[2]} m/s")
        else:
            print(f"Rocket is descending at {abs(self.rocket.velocity[2])} m/s", end="")
            if self.rocket.parachute_deployed:
                print(" under parachutes")
            else:
                print()

        print(f"It is currently {self.rocket.position[2]} meters in the air")


    def handle_frame(self):
        super().handle_frame()

        if not self.printed_rail_stats and self.rocket.position[2] > self.rocket.environment.rail_length:
            self.printed_rail_stats = True

            self.print(f"Off the rail, the rocket has {self.rocket.gees} gees")

        if self.rocket.descending and not self.turned:
            self.print('Reached the turning point at %.3s seconds with a height of %.5s meters' % (
                self.simulation.time, self.rocket.position[2]))
            self.turned = True
            self.print('The highest velocity during ascent was %.1f m/s, and the highest mach number was %.2f' % (
                self.simulation.max_velocity, self.simulation.max_mach))


        if not self.printed_thrusted and self.rocket.motor.finished_thrusting:
            self.print('Finished thrusting after %.3s seconds' % self.simulation.time)
            self.printed_thrusted = True

        if self.rocket.landed:
            self.print(
                "Rocket landed with a speed of %.3s m/s after %.4s seconds of flight time" %
                (magnitude(self.rocket.velocity),
                 self.simulation.time))
