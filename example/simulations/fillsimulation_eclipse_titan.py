

from src.simulation.fill.simulation import FillSimulation



if __name__ == "__main__":
    def flow_rate(sim: FillSimulation):
        return 1

    sim = FillSimulation()
    sim.flow_rate = flow_rate

    sim.run_simulation()