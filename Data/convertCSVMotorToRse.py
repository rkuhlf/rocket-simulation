# CREATE RSE FILE
# Using thrust, a proportional decrease in mass, and a mass-center-of-gravity lookup
# TODO: refactor this to use the new logger system, with a custom logger export definition for rse

import os
import pandas as pd

from Helpers.general import interpolate
from Helpers.data import interpolated_lookup, riemann_sum
from xml.dom import minidom


def initialize_motor_xml(min_mass, max_mass, name="customThrustCurve", length=3940, diameter=171):
    root = minidom.Document()

    database = root.createElement('engine-database')
    root.appendChild(database)

    engineList = root.createElement('engine-list')
    database.appendChild(engineList)

    motor = root.createElement("engine")
    motor.setAttribute("Type", "hybrid")
    motor.setAttribute("mfg", "Goddard")
    motor.setAttribute("code", name)
    motor.setAttribute("auto-calc-cg", "0")
    motor.setAttribute("auto-calc-mass", "0")
    motor.setAttribute("len", str(length))
    motor.setAttribute("dia", str(diameter))
    motor.setAttribute("initWt", str(max_mass))
    motor.setAttribute("propWt", str(max_mass - min_mass))
    engineList.appendChild(motor)

    data = root.createElement("data")
    motor.appendChild(data)

    return root, data

def save_root_xml(root, path: str):
    xml_str = root.toprettyxml(indent ="\t")

    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))

    with open(path, "w+") as f:
        f.write(xml_str)

def create_row_xml(root, row, mass, cg):
    eng_data = root.createElement("eng-data")
    eng_data.setAttribute("t", str(row["time"]))
    eng_data.setAttribute("f", str(row["thrust"]))
    
    eng_data.setAttribute("m", str(mass))
    eng_data.setAttribute("cg", str(cg))

    return eng_data

def create_linearly_interpolated_CG(CG_data_file, thrust_data_file, output_path, use_every=1):
    """Using mass-CG calculations as a lookup table, calculates the CG over time given a thrust curve.
    It will save it every :param use_every frames"""

    mass_CG_lookup = pd.read_csv(CG_data_file)

    # Convert from kg to g for RSE
    mass_CG_lookup["mass"] *= 1000
    max_mass = mass_CG_lookup["mass"][0]
    min_mass = mass_CG_lookup["mass"][len(mass_CG_lookup["mass"]) - 1]

    thrust_profile = pd.read_csv(thrust_data_file)
    total_impulse = riemann_sum(thrust_profile["time"], thrust_profile["thrust"])
    
    root, data = initialize_motor_xml(min_mass, max_mass)
    
    current_total = 0

    prev_time = 0
    prev_thrust = 0

    for i in range(0, len(thrust_profile), use_every):
        row = thrust_profile.iloc[i]
        current_total += (row["time"] - prev_time) * (row["thrust"] + prev_thrust) / 2

        # As we move up to the total impulse, we should be moving down to the min mass
        mass = interpolate(current_total, 0, total_impulse, max_mass, min_mass)
        # Convert to mm
        cg = 1000 * interpolated_lookup(mass_CG_lookup, "mass", mass, "CG", safe=True)

        data.appendChild(create_row_xml(root, row, mass, cg))

        prev_thrust = row["thrust"]
        prev_time = row["time"]

    save_root_xml(root, output_path)

def convert_full_csv_to_rse(csv_path, output_path, use_every=30, **kwargs):
    """Pass optional name, length, and diameter parameters
    In mm"""
    motor_data = pd.read_csv(csv_path)

    # Convert from kg to g for RSE
    motor_data["propellant_mass"] *= 1000
    # Convert to mm
    motor_data["propellant_CG"] *= 1000

    max_mass = motor_data["propellant_mass"].iloc[0]
    min_mass = motor_data["propellant_mass"].iloc[-1]
    
    root, data = initialize_motor_xml(min_mass, max_mass, **kwargs)

    end = len(motor_data) - 1
    for i in list(range(0, end, use_every)) + [end]:
        row = motor_data.iloc[i]

        mass = row["propellant_mass"]
        cg = row["propellant_CG"]

        data.appendChild(create_row_xml(root, row, mass, cg))

    save_root_xml(root, output_path)

def convert_csv_folder_to_rse(csv_folder_path, output_folder_path, name_prefix="MonteCarloMotor", **kwargs):
    
    # iterate over files in
    # that directory
    for i, filename in enumerate(os.scandir(csv_folder_path)):
        print(i)
        if filename.is_file():
            try:
                convert_full_csv_to_rse(filename.path, output_folder_path + f"/{i}.rse", name=f"{name_prefix}{i}", **kwargs)
            except Exception as e:
                print("Skipping because exception")
                print(e)

if __name__ == "__main__":
    # create_linearly_interpolated_CG("Data/Input/massCGLookup.csv", "Data/Input/ThrustCurves/currentGoddard.csv", "Data/Input/finleyThrust.rse")

    # convert_full_csv_to_rse("Data/Input/1 copy.csv", "Data/Input/newMotor.rse", length=3810)
    convert_csv_folder_to_rse("Analysis/MotorMonteCarloFiftyPercent", "Data/Input/ThrustCurves/RSEMotorsFiftyPercent-Temporary", name_prefix="50percent")
    convert_csv_folder_to_rse("Analysis/MotorMonteCarloSeventyFive", "Data/Input/ThrustCurves/RSEMotorsSeventyFivePercent-Temporary", name_prefix="75percent")

    pass



