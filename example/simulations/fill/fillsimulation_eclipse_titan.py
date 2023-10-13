

from src.rocketparts.motorparts.injector import find_mass_flow_single_phase_incompressible
from src.rocketparts.motorparts.oxtank import OxTank
from src.simulation.fill.simulation import FillSimulation
from example.constants import output_path

from example.visualization.sim_analysis.fill_visualization import display_optical_analysis
import numpy as np

from src.data.input.chemistry.nitrousproperties import get_liquid_nitrous_density



if __name__ == "__main__":
    def flow_rate(sim: FillSimulation):
        pressure_drop = sim.fill_tank.pressure - sim.run_tank.pressure
        # "21 injector holes, each with a 0.0902 in diameter"
        area = 21 * np.pi * (0.00229108 / 2) ** 2

        density = get_liquid_nitrous_density(fill_tank.temperature)
        return find_mass_flow_single_phase_incompressible(density, pressure_drop, area, 0.8)
    
    # Assuming one fully-filled tank.
    fill_tank = OxTank(length=1.7, diameter=0.254, ox_mass=100)
    run_tank = OxTank(length=2, diameter=0.152, ox_mass=0)

    sim = FillSimulation(fill_tank=fill_tank, 
                         run_tank=run_tank,
                         time_step=0.2)
    sim.flow_rate = flow_rate
    sim.logger.full_path = f"{output_path}/fillOutput.csv"

    sim.run_simulation()

    display_optical_analysis(sim.logger.full_path)