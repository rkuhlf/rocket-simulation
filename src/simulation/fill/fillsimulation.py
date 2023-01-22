


from src.rocketparts.motorparts.oxtank import OxTank
from lib.simulation import Simulation
from lib.general import constant


class FillSimulation(Simulation):
    def __init__(self, **kwargs):
        """
        fill_tank is the tank being emptied.
        run_tank is the tank being filled.
        flow_rate is the function to determine the flow rate out of the fill_tank. The entire FillSimulation object is passed to it. It should return a value in kg/s.
        head_loss is the function that calculates the pressure loss from fill_tank to run_tank. It should return a value in bar.
        
        """
        self.fill_tank = OxTank()
        self.run_tank = OxTank()
        self.head_loss = constant(5e5) # 5 bar
        self.flow_rate = constant(1)

        

        super().__init__(**kwargs)

    def simulate_step(self):
        mass_change = self.flow_rate(self)
        self.fill_tank.update_drain(mass_change)
        self.run_tank.update_drain(-mass_change)

        return super().simulate_step()

    
    @property
    def should_continue_simulating(self):
        """This should be overridden, otherwise it will always go to the max frames"""
        self


        return True

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, e):
        self._environment = e

        self.override_subobjects()


    def copy(self):
        new_environment = self.environment.copy()

        if self.logger is not None:
            new_logger = self.logger.copy()
        else:
            new_logger=None

        return FillSimulation(logger=new_logger, environment=new_environment)