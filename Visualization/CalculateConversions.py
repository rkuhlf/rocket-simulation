# CALCULATE CONVERSIONS FOR THE CURRENT OUTPUT
# Most of these are super inefficient but I dont really care since its just conversions

import os
import pandas as pd
import numpy as np
import re # FIXME: leave a comment that says what this is

from Helpers.general import numpy_from_string

# For each one, check if there is already a 'conversions.csv' in outputs
# Then add the conversions based on that data
# If not, make one based on output.csv

# Separate function to make a new conversions.csv based on output.csv if that is needed

input_file = 'Data/Output/output.csv'
output_file = 'Data/Output/conversions.csv'


def make_conversions_file():
    """Save all of the values in the input_file to their converted values in the output file"""
    # just copy output.csv to conversions.csv
    # Overwrites any already existing conversions
    df = pd.read_csv(input_file, index_col='time')
    df.to_csv(output_file)
    return df


def get_current_conversions():
    # Check if conversions exists
    if os.path.exists(output_file):
        # if it does, return it
        return pd.read_csv(output_file, index_col='time')
    else:
        # otherwise make a new one
        return make_conversions_file()


def convert_g_force():
    df = get_current_conversions()
    df['acceleration'] = df['acceleration'].apply(numpy_from_string)

    df['g-force'] = df['acceleration']
    df['g-force'] = df['g-force'].apply(lambda x: np.linalg.norm(x) / 9.81)
    df.to_csv(output_file)


def convert_mach():
    # FIXME: fix this so that it adjusts for altitude using the airQualities.csv file
    df = get_current_conversions()
    df['velocity'] = df['velocity'].apply(numpy_from_string)

    df['mach'] = df['velocity'].apply(
        lambda x: np.linalg.norm(x) / 343)  # this 343 should vary

    df.to_csv(output_file)


feet_per_meter = 3.28084


def convert_imperial():
    # feet and miles per second rather than meters
    df = get_current_conversions()

    df['position'] = df['position'].apply(numpy_from_string)
    df['velocity'] = df['velocity'].apply(numpy_from_string)
    df['acceleration'] = df['acceleration'].apply(numpy_from_string)


    df['imperial position'] = df['position'].apply(
        lambda x: x * feet_per_meter)
    df['imperial velocity'] = df['velocity'].apply(
        lambda x: x * feet_per_meter)
    df['imperial acceleration'] = df['acceleration'].apply(
        lambda x: x * feet_per_meter)

    df.to_csv(output_file)


def add_all_conversions():
    convert_g_force()
    convert_mach()
    convert_imperial()


if __name__ == '__main__':
    # make_conversions_file()
    add_all_conversions()
