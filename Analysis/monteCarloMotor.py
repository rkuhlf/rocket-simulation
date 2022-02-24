# Monte carlo base class for motor simulations

from typing import List
import numpy as np
import matplotlib.pyplot as plt
from Helpers.data import hist_box_count

from RocketParts.motor import CustomMotor
from monteCarlo import MonteCarlo
from Simulations.DesignedMotor2022 import get_randomized_sim
from simulation import MotorSimulation


# TODO: create some sensitivity analysis functions that find correlations in the characteristic figures.
class MonteCarloMotor(MonteCarlo):
    def __init__(self, sims: "List[MotorSimulation]"=[]):
        super().__init__(sims=sims)

        self.supercritical_nitrous_count = 0

    def initialize_simulation(self):
        sim = get_randomized_sim()
        sim.grain.verbose = False
        return sim

    def save_simulation(self, sim: MotorSimulation):
        super().save_simulation(sim)

        m: CustomMotor = sim.motor

        self.characteristic_figures.append({
            "Total Impulse": sim.total_impulse,
            "Total Specific Impulse": sim.total_specific_impulse,
            "Used Specific Impulse": sim.used_specific_impulse,
            "Burn Time": sim.burn_time,
            "Average Thrust": sim.average_thrust,
            # Inputs also listed here so it is easier to determine which have the most influence
            "Combustion Efficiency": m.cstar_efficiency,
            "Launch Temperature": m.ox_tank.initial_temperature,
            "Average OF": m.average_OF,
            "Average Regression": m.average_regression_rate,
            "Discharge Coefficient": m.injector.discharge_coefficient,
            "Length Regressed": m.fuel_grain.geometry.length_regressed,
        })

        data = sim.logger.get_dataframe()

        # "thrust", "combustion_chamber.pressure", "ox_tank.pressure", "combustion_chamber.temperature", "ox_tank.temperature", "combustion_chamber.fuel_grain.port_diameter", "OF", "combustion_chamber.cstar", "specific_impulse", "fuel_flow", "ox_flow", "mass_flow", "mass_flow_out", "combustion_chamber.ideal_gas_constant", "propellant_mass", "propellant_CG"
        data = data[["thrust", "OF", "ox_tank.pressure", "ox_tank.temperature", "combustion_chamber.temperature", "propellant_mass", "propellant_CG"]].copy()

        self.important_data.append(data)

    def handle_failed_sim(self, sim, e):
        if e is ValueError:
            self.supercritical_nitrous_count += 1
        
        return super().handle_failed_sim(sim, e)

    def finish_simulating(self):
        super().finish_simulating()
        # FIXME: Perhaps not correct, if something else gives ValueError. I need custom error methods
        print(f"Nitrous went supercritical {self.supercritical_nitrous_count} times")


    #region Characteristic Figure Displays
    # TODO: change this to a more general logger class that has all of these analysis functions and can read in simulations using a function or can simply accept some pandas arrays
    def plot_overview(self):
        df = self.characteristic_figures_dataframe

        plt.scatter(df["Burn Time"], df["Total Impulse"])

        plt.title("Motor Comprehensive Monte Carlo")
        plt.xlabel("Burn Time (s)")
        plt.ylabel("Total Impulse (Ns)")

        plt.show()
    
    def plot_efficiency(self):
        df = self.characteristic_figures_dataframe

        # FIXME: This graph is no longer working int(np.sqrt(2 * len(df.index)))
        plt.hist(df[["Total Specific Impulse", "Used Specific Impulse"]].transpose(), 3, density=True, histtype='bar', label=["Total Specific Impulse", "Used Specific Impulse"])
        plt.legend()

        plt.title("Monte Carlo Motor Efficiencies")
        plt.xlabel("Efficiency [s]")
        plt.ylabel("Frequency")

        plt.show()
    
    def plot_average_thrust(self):
        df = self.characteristic_figures_dataframe

        plt.scatter(df["Total Impulse"], df["Average Thrust"])

        plt.title("Monte Carlo Motor Average Thrust")
        # We should be aiming for all of the average thrust values to be above a certain threshold, which will give us a good liftoff, and we want everything to be as far to the right as possible
        plt.ylabel("Average Thrust (N)")
        plt.xlabel("Total Impulse (Ns)")

        plt.show()

    def plot_cstar_impulse_correlation(self):
        df = self.characteristic_figures_dataframe

        plt.scatter(df["Combustion Efficiency"], df["Total Impulse"])

        plt.title("Monte Carlo C* Efficiency Importance")
        plt.xlabel("C* Efficiency ()")
        plt.ylabel("Total Impulse (Ns)")

        plt.show()
    
    def plot_cstar_time_correlation(self):
        df = self.characteristic_figures_dataframe

        plt.scatter(df["Combustion Efficiency"], df["Burn Time"])

        plt.title("Monte Carlo C* Efficiency Importance")
        plt.xlabel("C* Efficiency ()")
        plt.ylabel("Burn Time (s)")

        plt.show()
    
    def plot_discharge_correlation(self):
        df = self.characteristic_figures_dataframe

        plt.scatter(df["Discharge Coefficient"], df["Total Impulse"])

        plt.title("Monte Carlo Discharge Importance")
        plt.xlabel("Discharge Coefficient ()")
        plt.ylabel("Total Impulse (Ns)")

        plt.show()
    
    def plot_OF_correlation(self):
        df = self.characteristic_figures_dataframe

        plt.scatter(df["Average OF"], df["Total Impulse"])

        plt.title("Monte Carlo OF Importance")
        plt.xlabel("O/F ()")
        plt.ylabel("Total Impulse (Ns)")

        plt.show()
    
    def plot_regression_correlation(self):
        df = self.characteristic_figures_dataframe

        # Convert from m to mm
        plt.scatter(df["Average Regression"] * 1000, df["Total Impulse"])

        plt.title("Monte Carlo Regression Rate Importance")
        plt.xlabel("Regression Rate (mm/s)")
        plt.ylabel("Total Impulse (Ns)")

        plt.show()
        
    def plot_regressed(self):
        df = self.characteristic_figures_dataframe

        # Convert from m to mm
        plt.hist(df["Length Regressed"] * 1000, hist_box_count(len(df)))

        plt.title("Distribution of Ending Regression")
        plt.xlabel("Length Regressed (mm)")

        plt.show()
    
    #endregion

    def plot_thrust_curves(self):
        for df in self.important_data:
            plt.plot(df.index, df["thrust"])
        
        plt.title("Thrust Curves")
        plt.xlabel("Time (s)")
        plt.ylabel("Thrust (N)")

        plt.show()
    
    def plot_mass_movement(self):
        for df in self.important_data:
            plt.plot(df.index, df["propellant_CG"])
        
        plt.title("CG Curves")
        plt.xlabel("Time (s)")
        plt.ylabel("Distance (m)")

        plt.show()
    

def run_analysis(count=100, folder="Analysis/MotorMonteCarlo-Temporary"):
    m = MonteCarloMotor()
    m.simulate_randomized(count)

    m.print_characteristic_figures()

    # time is logged automatically because it is the index
    # "thrust", "combustion_chamber.pressure", "ox_tank.pressure", "combustion_chamber.temperature", "ox_tank.temperature", "combustion_chamber.fuel_grain.port_diameter", "OF", "combustion_chamber.cstar", "specific_impulse", "fuel_flow", "ox_flow", "mass_flow", "mass_flow_out", "combustion_chamber.ideal_gas_constant"
    m.save_important_data(folder)

    m.save_characteristic_figures(f"{folder}/output.csv")

    return m

    

def display_analysis(motorSim: MonteCarloMotor):
    motorSim.plot_overview()
    motorSim.plot_efficiency()
    motorSim.plot_average_thrust()
    motorSim.plot_thrust_curves()

    motorSim.plot_cstar_impulse_correlation()
    motorSim.plot_OF_correlation()
    motorSim.plot_regression_correlation()



# FIXME: debug the NaN values that occasionally come up
if __name__ == "__main__":
    m = run_analysis(100, "Analysis/MotorMonteCarlo75cm-Temporary")

    display_analysis(m)

    pass

