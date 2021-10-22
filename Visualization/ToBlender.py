# CONVERT FLIGHT SIMULATION TO BLENDER ANIMATION
# This file is intended to be run inside of the scripts section of a Blender project.
# It converts a csv of output into a flight path for an object
# Note that installing pandas for Blender is not a simple task. I believe you can either configure the python version used to do some really janky stuff to get it installed on the original.


import bpy
import csv
import os
from math import pi
import pandas as pd

scene = bpy.context.scene

if (len(bpy.context.selected_objects) == 0):
    print("You haven't selected an object")
    raise Exception('You must select the rocket object')

rocket = bpy.context.selected_objects[0]


filename = 'noWind.csv'
directory = r'C:\Users\riley\Documents\PythonPrograms\MathModels\Rocket\rocket-simulation\Data\Output'  # <-- if you have linux or osx
# directory = r'c:\some\directory'  # <-- if windows, the r is important
# directory = 'c:/some/directory'  # <-- if windows (alternative)

fullpath = os.path.join(directory, filename)

data = pd.read_csv(fullpath)

for index, row in data.iterrows():
    # adjusting the multiplier should give some control over frame rate
    scene.frame_set(index * 1)

    x = float(row.loc['position1'])
    y = float(row.loc['position2'])
    z = float(row.loc['position3'])

    rocket.location = (x, y, z)
    rocket.keyframe_insert(data_path="location", index=-1)
    
    
    # rotation around
    z = float(row['rotation1'])
    # rotation down
    y = float(row['rotation2'])
    
    # There is no extra roll rotation, because blender and I do things differently. It will probably take some advanced math to figure out this last bit
#    z = float(row['rotation3'])

    rocket.rotation_euler  = (0, y, z)
    rocket.keyframe_insert(data_path="rotation_euler", index=-1)
