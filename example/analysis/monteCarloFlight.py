
from matplotlib import pyplot as plt
from Analysis.MonteCarloFlightData.AnalyzeMonteCarloFlight import display_altitude_lines, display_apogee_distribution, display_deployment_distribution, display_landing, display_max_mach_distribution, display_max_velocity, display_total_impulse_effect
from Analysis.monteCarlo import MonteCarlo
from lib.data import hist_box_count
from Simulations.DesignedRocket import get_randomized_sim
from lib.simulation import RocketSimulation


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

    

    def display_overview(self):
        df = self.characteristic_figures_dataframe

        display_apogee_distribution(df)
    
    def display_landing(self):
        df = self.characteristic_figures_dataframe

        display_landing(df)
    
    def display_impulse_correlation(self):
        df = self.characteristic_figures_dataframe

        display_total_impulse_effect(df)
    
    def display_max_velocity(self):
        df = self.characteristic_figures_dataframe

        display_max_velocity(df)
        
            
    def display_lateral_velocity(self):
        df = self.characteristic_figures_dataframe

        display_deployment_distribution(df)
    
    def display_max_mach(self):
        df = self.characteristic_figures_dataframe

        display_max_mach_distribution(df)

    def display_altitude_curves(self):

        display_altitude_lines(self.important_data)

    