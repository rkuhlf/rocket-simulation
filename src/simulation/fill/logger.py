from src.constants import output_path

from lib.logger import FeedbackLogger
from lib.general import magnitude
from src.simulation.fill.logger_features import *
from src.rocketparts.motorparts.oxtank import OxTank

class FillLogger(FeedbackLogger):
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


    @property
    def fill_tank(self) -> OxTank:
        return self.simulation.fill_tank

    @fill_tank.setter
    def fill_tank(self, tank):
        self.simulation.fill_tank = tank

    @property
    def run_tank(self) -> OxTank:
        return self.simulation.run_tank

    @run_tank.setter
    def run_tank(self, tank):
        self.simulation.run_tank = tank

    def display_partial_data(self):
        super().display_partial_data()


        print(f"Fill tank ({} kg, {self.fill_tank.pressure}) draining at {} kg/s")
        # They might fill at slightly different rates because the run tank is also venting.
        print(f"Run tank ({} kg, {self.run_tank.pressure}) filling at {} kg/s")


    def handle_frame(self):
        return super().handle_frame()
