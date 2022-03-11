
from matplotlib import pyplot as plt
from Analysis.monteCarlo import MonteCarlo
from Helpers.data import hist_box_count
from Simulations.DesignedRocket import get_randomized_sim
from simulation import RocketSimulation


class MonteCarloFlight(MonteCarlo):
    def __init__(self, sims=[]):
        super().__init__(sims=sims)

    def initialize_simulation(self):
        sim = get_randomized_sim()
        return sim

    def save_simulation(self, sim: RocketSimulation):
        super().save_simulation(sim)

        self.characteristic_figures.append({
            "Apogee": sim.apogee,
            "Lateral Velocity": sim.apogee_lateral_velocity,
            "Total Impulse": sim.rocket.motor.total_impulse,
            "Max Mach": sim.max_mach,
            "Max Velocity": sim.max_velocity,
            "Landing Speed": sim.landing_speed,
            "Landing Distance": sim.dist_from_start,
        })

        data = sim.logger.get_dataframe()

        # 'position', 'velocity', 'acceleration', 'rotation', 'angular_velocity', 'angular_acceleration'
        data = data[["position3"]].copy()

        self.important_data.append(data)

    def finish_simulating(self):
        super().finish_simulating()
        # TODO: create count of tumbling rockets

    
    # TODO: Convert the other monte carlo analysis to be included in something like this
    # TODO: write this. And a method to read in from a path
    def add_characteristic_figures(self, new_characteristic_figures):
        pass

    

    def plot_overview(self):
        df = self.characteristic_figures_dataframe

        plt.scatter(df["Lateral Velocity"], df["Apogee"])

        plt.title("Monte Carlo with Motors")
        plt.xlabel("Lateral Velocity (m/s)")
        plt.ylabel("Apogee (m)")

        plt.show()
    
    def plot_landing(self):
        df = self.characteristic_figures_dataframe

        plt.scatter(df["Landing Distance"], df["Landing Velocity"])

        plt.title("Landing Analysis")
        plt.ylabel("Landing Velocity (m/s)")
        plt.xlabel("Landing Distance (m)")

        plt.show()
    
    def plot_impulse_correlation(self):
        df = self.characteristic_figures_dataframe

        plt.scatter(df["Total Impulse"], df["Apogee"])

        plt.title("Total Impulse Importance")
        plt.xlabel("Total Impulse (Ns)")
        plt.ylabel("Apogee (m)")

        plt.show()
    
    def plot_max_velocity(self):
        df = self.characteristic_figures_dataframe

        plt.hist(df[["Max Velocity"]], hist_box_count(len(df)), histtype='bar')

        plt.title("Range of Max Velocities")
        plt.xlabel("Max Velocity (m/s)")
        plt.ylabel("Frequency")

        plt.show()
            
    def lateral_velocity(self):
        df = self.characteristic_figures_dataframe

        plt.hist(df[["Lateral Velocity"]].transpose(), hist_box_count(len(df.index)), density=True, histtype='bar')

        plt.title("Range of Lateral Velocities")
        plt.xlabel("Lateral Velocity (m/s)")
        plt.ylabel("Frequency")

        plt.show()
    
    def plot_max_mach(self):
        df = self.characteristic_figures_dataframe

        plt.hist(df[["Max Mach"]], hist_box_count(len(df)), histtype='bar')

        plt.title("Range of Max Mach Numbers")
        plt.xlabel("Max Mach ()")
        plt.ylabel("Frequency")

        plt.show()

    def plot_altitude_curves(self):
        for df in self.important_data:
            plt.plot(df["time"], df["altitude"])
        
        plt.title("Flights")
        plt.xlabel("Time (s)")
        plt.ylabel("Alitude (m AGL)")

        plt.show()

    