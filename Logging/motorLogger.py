
from Logging.customLogger import CustomLogger


class MotorLogger(CustomLogger):
    """
        Logs the progress of the custom motor simulation along with some print statements.
    """

    def __init__(self, motor, **kwargs):
        # You need to make sure the parent's override doesn't override the self values we have already established
        super().__init__(motor)

        # TODO: it would be nice to have the average molar mass of the products displayed
        self.to_record = ["thrust", "combustion_chamber.pressure", "ox_tank.pressure", "combustion_chamber.temperature", "ox_tank.temperature", "combustion_chamber.fuel_grain.port_diameter", "OF", "combustion_chamber.cstar", "specific_impulse", "fuel_flow", "ox_flow", "mass_flow", "mass_flow_out", "combustion_chamber.ideal_gas_constant"]

        self.debug_every = 2 # seconds

        self.overwrite_defaults(**kwargs)

        self.printed_pressurized = False
        # Print every time it switches
        self.overexpanded = True

        self.initial_pressure = self.motor.ox_tank.pressure

    @property
    def motor(self):
        return self.logging_object

    @motor.setter
    def motor(self, m):
        self.logging_object = m

    def display_partial_data(self):
        print(f"Ox Tank pressure {self.motor.ox_tank.pressure} Pascals")
        print(f"Chamber pressure {self.motor.combustion_chamber.pressure} Pascals")

        return super().display_partial_data()
        
    def handle_frame(self):
        super().handle_frame()

        if not self.printed_pressurized and not self.motor.combustion_chamber.pressurizing:
            print(f"Motor finished pressurizing to {self.motor.combustion_chamber.pressure} Pa at {self.motor.environment.time}")
            self.printed_pressurized = True


    def save_to_csv(self):
        # Give some information about how we are looking a the end of the burn

        print(f"The motor finished with {self.motor.combustion_chamber.fuel_grain.fuel_mass} kg of fuel and {self.motor.combustion_chamber.fuel_grain.outer_radius - self.motor.combustion_chamber.fuel_grain.port_radius} meters left")

        print(f"There is {self.motor.ox_tank.ox_mass} kg of oxidizer left and there is still a pressure difference of {self.motor.ox_tank.pressure - self.motor.combustion_chamber.pressure} Pa")

        return super().save_to_csv()
