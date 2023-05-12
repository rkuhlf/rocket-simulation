

from src.simulation.fill.simulation import FillSimulation
from example.constants import output_path


if __name__ == "__main__":
    def flow_rate(sim: FillSimulation):
        return 1

    sim = FillSimulation(time_step=0.2)
    sim.flow_rate = flow_rate
    sim.logger.full_path = f"{output_path}/fillOutput.csv"

    sim.run_simulation()