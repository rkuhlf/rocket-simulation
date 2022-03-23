# Monte carlo base class for motor simulations

from typing import List
import matplotlib.pyplot as plt
from Analysis.OpticalAnalysisMotorMonteCarlo import display_CG_movement, display_OF_correlation, display_average_thrust, display_cstar_importance, display_curves, display_regression, display_efficiency, display_overview

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
            "Average OF": m.average_OF,
            "Average Regression": m.average_regression_rate,
            "Length Regressed": m.fuel_grain.geometry.length_regressed,
            # Inputs also listed here so it is easier to determine which have the most influence
            "Combustion Efficiency": m.cstar_efficiency,
            "Launch Temperature": m.ox_tank.initial_temperature,
        })

        data = sim.logger.get_dataframe()

        try:
            # "thrust", "combustion_chamber.pressure", "ox_tank.pressure", "combustion_chamber.temperature", "ox_tank.temperature", "combustion_chamber.fuel_grain.port_diameter", "OF", "combustion_chamber.cstar", "specific_impulse", "fuel_flow", "ox_flow", "mass_flow", "mass_flow_out", "combustion_chamber.ideal_gas_constant", "propellant_mass", "propellant_CG"
            data = data[["thrust", "OF", "ox_tank.pressure", "ox_tank.temperature", "combustion_chamber.temperature", "propellant_mass", "propellant_CG", "combustion_chamber.fuel_grain.geometry.length_regressed", "nozzle.exit_pressure"]].copy()

            self.important_data.append(data)
        except KeyError:
            print("The data requested by the motor monte carlo was not saved by the motor. Try modifying the MotorLogger")
            raise

    def handle_failed_sim(self, sim, e):
        if e is ValueError:
            self.supercritical_nitrous_count += 1
        
        return super().handle_failed_sim(sim, e)

    def finish_simulating(self):
        super().finish_simulating()
        # FIXME: Perhaps not correct, if something else gives ValueError. I need custom error methods
        print(f"Nitrous went supercritical {self.supercritical_nitrous_count} times")


    #region Plots/Displays
    # TODO: change this to a more general logger class that has all of these analysis functions and can read in simulations using a function or can simply accept some pandas arrays
    def plot_overview(self):
        df = self.characteristic_figures_dataframe

        display_overview(df)
    
    def plot_efficiency(self):
        df = self.characteristic_figures_dataframe
        display_efficiency(df)
    
    def plot_average_thrust(self):
        df = self.characteristic_figures_dataframe
        display_average_thrust(df)

    def plot_cstar_importance(self):
        df = self.characteristic_figures_dataframe
        display_cstar_importance(df)
    
    def plot_OF_correlation(self):
        df = self.characteristic_figures_dataframe
        display_OF_correlation(df)
        
    def plot_regression(self):
        display_regression(self.characteristic_figures_dataframe, self.important_data)

    def plot_thrust_curves(self):
        # FIXME: not working - variable not found maybe
        display_curves(self.important_data)
    
    def plot_mass_movement(self):
        display_CG_movement(self.important_data)
    
    #endregion

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
    # More analysis available in opticalAnalysisMotorMonteCarlo
    motorSim.plot_overview()
    motorSim.plot_efficiency()
    motorSim.plot_average_thrust()
    motorSim.plot_thrust_curves()

    motorSim.plot_cstar_importance()
    motorSim.plot_OF_correlation()
    motorSim.plot_regression()



# FIXME: debug the NaN values that occasionally come up
if __name__ == "__main__":
    m = run_analysis(3, folder="Analysis/MotorMonteCarloAccurateLoadDistribution")

    display_analysis(m)

    pass

