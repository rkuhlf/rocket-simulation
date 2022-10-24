# Horizon 1: Python Simulations and Analysis

This repository is a collection of all of the code I wrote for Brazoswood's 2021-2022 Goddard program. Each year, we build a hybrid rocket from the ground up, launching it at the WSMR missile range after the school year. The program has improved steadily, with 5/5 successful flights, reaching 35,000" in 2021 and 43,000" in 2022.

However, there are many different problems that the design process entails. There are scripts in the repository for design optimization, simulation, and post-flight analysis. Though it is possible, the code was not written with the intention of being used as a library, rather as a reference for future years - if a future year faces a problem with using Python in the design process, they can find Goddard 2022's solution here.

## User Guide

If you would like to use the code to simulate your rocket, there are several things that must be input input. After the repository is closed, you should open up the *SimulateRocket* file. This file is the main entrypoint for running a basic flight simulation, although you could easily use similar code in a different file to have the same effect.

To run either a rocket or a motor simulation, you need to have an `Environment` object. It will tells any simulation the `time_increment` and the atmospheric conditionss, including wind. The rocket also needs a motor, so you can either pass in an instance of `CustomMotor` (simulating all the combustion by hand) or you can specify a pre-defined thrust curve in the `Motor` class. Parachutes are also passed in as a separate list of `Parachute` objects.

Once your rocket is ready to go, there are several helper classes that loop through the frames of the flight: `Simulation` to iteratively sum forces and update the physics, and `Logger` to store the data and print events. Once all of the classes have been initialized and all references set, call `.run()` on the `Simulation` object. Here is a sample:

```python
from environment import Environment
from RocketParts.motor import Motor
from rocket import Rocket
from RocketParts.parachute import ApogeeParachute, Parachute
from logger import RocketLogger 
from simulation import RocketSimulation

env = Environment({"time_increment": 0.1})
motor = Motor()
drogue_parachute = ApogeeParachute({"radius": 0.2})
main_parachute = Parachute()
rocket = Rocket(environment=env, motor=motor, parachutes=[drogue_parachute, main_parachute])
logger = RocketLogger(
    rocket,
    ['position', 'velocity', 'acceleration', 'rotation', 'angular_velocity',
     'angular_acceleration'])

logger.splitting_arrays = True

sim = RocketSimulation(environment=env, rocket=rocket, logger=logger)

sim.run_simulation()
```

## Programming Conventions and Style

### Visualization

The graphing is done using MatPlotLib since it provided easy integration with Pandas and Numpy.

I also have a ToBlender.py file which can export your .csv file to Blender 3D. Unfortunately, that file must be run inside of Blender's code editor, so it is mostly here for completeness, running it by itself will throw lots of errors.

## Sources / Further Reading

- [Notes on Multiple Degrees of Freedom for Goddard 2021-2022](https://docs.google.com/document/d/1VEkxpdZ9q7t6uQZ0db8XvYZEkJN-9KKGfAi_a7vk-ag/edit?usp=sharing)
- I really think this [Topics in Advanced Model Rocketry](https://www.apogeerockets.com/Rocket_Books_Videos/Books/Topics_In_Advanced_Model_Rocketry) book would have been super helpful, but I could never get my hands on it.
- The designNotes.md file has most of the information about programming-oriented decisions that I made.
- [OpenRocket Technical Manual](http://openrocket.sourceforge.net/techdoc.pdf)
<!-- TODO: add in that pdf that TJ recommended -->


<!-- 
Some general todos for this project

Merge this random git branch with a ton of changes (and actually start making sure that the main banch can run everything)
Go back through every single file that has been written and is designed to be run, and make sure they work
Add repr methods for all of the classes

Redesign naming conventions for the motor file
Read back through this Readme and make sure that everything is correct; update the necessary stuff
move designNotes into a Documentation folder
Add a bunch more documentation
Add a Test to just run all of the main entry points for the thing and make sure they work okay

Create a simulation where the motor is actually hooked into the rocket

Move the motor simulation into its own folder

Go through and prioritize all of the other todos everywhere
-->



<!-- TODO: I need a refactor of how the variable names work for the logger. I think I will eventually end up passing logger objects around in lots of places, and you can use that logger object to read a data file that it created. The user will have to match the file to the logger. That way I can also make some objects for the Rasaero and openrocket loggers -->
<!-- TODO: I really need to implement testing before anything can be pushed to the main branch -->
<!-- TODO: I also need a separate class for things that have a radius that could also be set with a diameter. I could just have them inherit from an object. This is where MetaProgramming would be super nice, because I could allow the name to be custom -->
<!-- Ideally, there would be one rocket simulation class, which would be inherited both by my rocket simulation and by a wrapper for the OpenRocket simulation -->

<!-- I should explain that this is all of the code that I wrote. So it is not necessarily intended for use as a library or a replacement for OpenRocket. It is more for posterity's sake: if someone needs to figure out how I solved a problem, it will be in here. -->