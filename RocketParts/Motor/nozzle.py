class CustomMotor(Motor):
    # Test with https://www.grc.nasa.gov/www/k-12/rocket/ienzl.html
    # At the moment, everything is being calculated as a constant
    # I'm pretty sure it changes, but I haven't quite realized what gives.
    # Obviously it has something to do with the mass flow rate, since at some points there will be more material going through.
    # However, there doesn't appear to be any wiggle room for that in the equation

    def __init__(self, config={}):
        # TODO: Figure out how rocket motors work with gas (particularly hybrid) because I think it might affect these variables
        # pt is the total pressure in the combustion chamber, same for tt
        # I'm not sure these are the only things changing. I mean, there should be someway to simulate the fuel grain
        self.total_pressure = 10
        self.total_temperature = 100

        # Supposedly ratio should be from 1 to 60
        self.chamber_area = 0.1  # m
        self.throat_area = 0.01  # m
        self.exit_area = 0.1  # m

        # I believe that 1.33 is the best value for Nitrous, a common fuel
        # Between 1.3 and 1.6 ish
        self.specific_heat_ratio = 1.4  # often abbreviated gamma in equations
        self.gas_constant = 8.31446261815324  # per mole, probably not correct
        self.specific_heat_exponent = (
            self.specific_heat_ratio + 1) / (2 * (self.specific_heat_ratio - 1))

        super().overwrite_defaults(config)


    def mass_flow_rate(self, mach=1):
        # TODO: add mach adjustment into here
        # I believe this is for the conditions given that mass flow rate is choked at sonic conditions
        # I suspect this is where a CFD would be much more accurate
        # tis is were the problems are

        ans = self.throat_area * self.total_pressure / \
            (self.total_temperature) ** (1 / 2)

        ans *= (self.specific_heat_ratio / self.gas_constant) ** (1 / 2)

        ans *= ((self.specific_heat_ratio + 1) / 2) ** -self.specific_heat_exponent

        return ans
