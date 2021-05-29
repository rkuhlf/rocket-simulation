# This file is intended to be run inside of the scripts section of a blender project.
# It converts a csv of output into a flight path for an object


import bpy
import csv
import os
from math import pi

scene = bpy.context.scene

rocket = bpy.context.selected_objects[0]


filename = 'output.csv'
# <-- if you have linux or osx
directory = r'C:\Users\riley\Documents\PythonPrograms\MathModels\Rocket'
# directory = r'c:\some\directory'  # <-- if windows, the r is important
# directory = 'c:/some/directory'  # <-- if windows (alternative)

fullpath = os.path.join(directory, filename)

with open(fullpath, 'r', newline='') as csvfile:
    ofile = csv.reader(csvfile, delimiter=',')
    next(ofile)  # <-- skip the x,y,z header

    # this makes a generator of the remaining non-empty lines
    rows = (r for r in ofile if r)

#    for row in rows:
#        for i in row:
#            print(i)

    frame = 1
    for row in rows:
        scene.frame_set(frame)

        x = float(row[4])
        z = float(row[5])
        rotation = float(row[10])
        print(rotation)

        rocket.location = (x, 0, z)
        rocket.keyframe_insert(data_path="location", index=-1)

        rocket.rotation_euler = (0, rotation, 0)
        rocket.keyframe_insert(data_path="rotation_euler", index=-1)

        # Using this increment and the frame rate, you can manipulate it to be real time
        # Curently, every frame is 0.1 seconds
        frame += 1
