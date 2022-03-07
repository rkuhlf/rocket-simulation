import numpy as np
from builtins import print as builtin_print


from Helpers.decorators import diametered
from RocketParts.massObject import MassObject



@diametered(radius_name="bolt_radius", diameter_name="bolt_diameter")
class RetentionRing(MassObject):
    def __init__(self, **kwargs):
        self.mass = 0.63 # kg (from Fusion 3/7/22)
        self.bolt_count = 6
        self.bolt_radius = 0.00635 / 2
        self.target_safety_factor = 1.5
        self.bolt_shear_strength = 900_000_000 * 0.6 # Pa
        self.retention_ring_shear_strength = 900_000_000 * 0.6 # Pa
        self.retention_ring_compressive_strength = 250e6 # Pa
        # Width of the retention ring
        self.bolt_length_into_ring = 0.0127 * 3/4 # m; totally made up
        # The shortest length between the top of the retention ring and the middle of the top bolt
        self.bolt_minor_thickness = 0.0254

        # Force variables that should change frequently through a simulation
        # # https://workflowy.com/s/nozzle-retention/R3QmGFlhHrfeqdaw
        # shear load = abs(inner weight + base drag + internal pressure force - thrust - external weight - external drag)
        self.internal_load = 50_000 # N; all of the forces pushing down on the inside of the nozzle
        self.external_load = 600 # N; all of the forces pushing down on the outside of the shell

        self.overwrite_defaults(**kwargs)
    
    @property
    def bolt_area(self):
        return np.pi * self.bolt_radius ** 2

    @property
    def total_bolt_area(self):
        return self.bolt_count * self.bolt_area
    
    #region Safety Factor Calculations
    @property
    def bolt_shear_safety_factor(self):
        experienced_pressure = self.internal_load / self.total_bolt_area

        return self.bolt_shear_strength / experienced_pressure
    
    @property
    def tear_out_safety_factor(self):
        # It has to tear out on both sides of the bolt, and on the end
        individual_tear_out_area = self.bolt_length_into_ring * self.bolt_minor_thickness * 2
        individual_tear_out_area += self.bolt_diameter * self.bolt_minor_thickness
        experienced_pressure = self.internal_load / (individual_tear_out_area * self.bolt_count)

        return self.retention_ring_shear_strength / experienced_pressure
    
    @property
    def bearing_safety_factor(self):
        # It has to tear out on both sides of the bolt, and on the end
        individual_bearing_area = self.bolt_length_into_ring * self.bolt_diameter
        experienced_pressure = self.internal_load / (individual_bearing_area * self.bolt_count)

        return self.retention_ring_compressive_strength / experienced_pressure

    #endregion

    def check_safety_factor(self):
        print(f"Shear: {self.bolt_shear_safety_factor}")
        print(f"Tear Out: {self.tear_out_safety_factor}")
        print(f"Bearing: {self.bearing_safety_factor}")
    
    def __repr__(self) -> str:
        ans = ""
        ans += f"--- Retention Ring of Mass {self.mass:.2f} kg ---\n\n"

        ans += f"{self.bolt_count} bolts of {self.bolt_diameter * 39.3700787:.2f} inch diameter\n"

        ans += "SAFETY FACTORS: \n"
        ans += f"Shear: {self.bolt_shear_safety_factor}\n"
        ans += f"Tear Out: {self.tear_out_safety_factor}\n"
        ans += f"Bearing: {self.bearing_safety_factor}\n"

        return ans

# Tear out/bearing for the outside coupler piece will eventually be an issue with drag attempting to accelerate the outer shell more than accelerates the entire rocket 



if __name__ == "__main__":
    # The pressure is pi*(0.1651/2)^2 * 2500000
    # Tensile strength of steel alloy screw is 900000000 Pa (according to McMasterCarr), but I will use 60% for shear strength. 900_000_000 * 0.6
    # Tensile strength of aluminum is much worse than steel
    # I am going to look at a few diameters, but I think we are in the range of 3/8 inch
    # Highly sensitive to bolt diameter: 8 mm gives 30, 10 mm gives 20, 12 mm gives 14
    # Tanner said 620528156 Pa (90000 psi) was what he had been using for the strength of his bolts
    # (120 * 9.81, 600, 53520, 620528156, 0.00635, safety_factor=1))
    # only giving two for some reason
    
    # Total weight is based on the wet mass. It will actually be less. For a more complex calculation, it would have to be frame-by-frame # TODO: write code that does this in the Analysis folder
    # nozzle base drag is based on CD for base=0.25 out of CD total = 0.85, which is about 30%, then I multiplied it by the 2000 N at max drag

    retentionArgs = {
        "bolt_count": 10,
        "bolt_diameter": (3/8) / 39.3700787,
        # Steel default for shear strength is fine
        # Assuming 25 bar and using 6.78 for the ID
        "internal_load": np.pi * (0.172212/2)**2 * 2500000,
        # At 300 C stainless steel has 60% strength. 170 MPa is the base strength
        "retention_ring_compressive_strength": 170e6 * 0.6,
        "retention_ring_shear_strength": 170e6 * 0.6 * 0.6,
        # This is for alloy steel
        "bolt_shear_strength":  358e6 * 0.6 * 0.6
    }

    retention = RetentionRing(**retentionArgs)
    print(repr(retention))
