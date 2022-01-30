from Logging.customLogger import CustomLogger
from Logging.flightLogger import FlightLogger

class CustomFlightLogger(CustomLogger, FlightLogger):
    @rocket.setter
    def rocket(self, r):
        self.logging_object = r

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
                self.rocket.environment.time, self.rocket.position[2]))
            self.turned = True
            self.print('The highest velocity during ascent was %.1f m/s, and the highest mach number was %.2f' % (
                self.simulation.max_velocity, self.simulation.max_mach))


        if not self.printed_thrusted and self.rocket.motor.finished_thrusting:
            self.print('Finished thrusting after %.3s seconds' % self.rocket.environment.time)
            self.printed_thrusted = True

        if self.rocket.landed:
            self.print(
                "Rocket landed with a speed of %.3s m/s after %.4s seconds of flight time" %
                (magnitude(self.rocket.velocity),
                 self.rocket.environment.time))
