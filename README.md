# Horizon 1: Python Simulations and Analysis

This repository is basically a collection of all of the code I have written for Brazoswood's 2021-2022 Goddard program. Each year, we build a relatively large hybrid rocket from the ground up, launching it at White Sands, New Mexico after the school year. The program has improved steadily, with 5/5 successful flights, reaching 35,000" in 2021 and 43,000" in 2022.

## User Guide

If you would like to use the code to simulate your rocket, there are a few things you have to input. After you have cloned the repository, you should open up the *SimulateRocket* file. This file is the main entrypoint that I usually use to start run a basic flight simulation, but you could easily use similar code in a different file to have the same effect.

To run either a rocket or a motor simulation, you need to have an environment object. That will tell your simulation what the time increment is and what the atmospheric conditions are, including wind. The rocket also needs a motor, so you can either pass in a custom motor (simulating all the combustion stuff) or you can just use a default one where the thrust follows a pre-defined curve. Parachutes are also passed in separately.

Once your rocket is ready to go, I have built a couple of helper classes that loop through all of the frames, `Simulation` and to store the data as well as printing any important events `Logger`. Once you have initialized those, with all of the necessary objects passed in, you are good to go. Here is a sample:

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

I have tried to use object-oriented practices for all of the modelling. Each component from the fins to the body tube to the injector must be instantiated independently, then linked together by the rocket or motor class. For design, I went for a more functional approach. In my naming conventions, I have attempted to keep clear practices for determing the name of each function. Within a class, if a function returns a value, it should begin with *get_*, but if it has side effects it should be *calculate_*. For optimization design functions, the prefix is *determine_*, but for general purpose design functions and helper functions, you should use *find_*.

I have tried to use the *if __name__ == "__main__" idiom wherever a file has code that is meant to be run. In addition, files that should be run begin with a capital letter, as well as all folder names.

There are many ways to program multiple objects so that they take data differently but perform the same calculations on it. At the moment, I am trying to have the main parent object for a class always accept a few different kinds of `set_` function, like `set_constant_mass` or `set_CG_function` or `set_thrust_table`. However, implementing these must always result in a change to the properties of the object, otherwise preset object will not be able to save it properly.

This readme file is really long, so I have more information about the design practices listed under a designNotes.md file.

### A Note on Preset Object

The idea is that eventually everything will be saveable. Also it allows the settings to be passed in as a config argument. I know there are other idioms like *kwargs that may be better suited for this, I might swap everything out later.

I think there is a half-finished attempt to implement something like that saving feature buried somewhere in here.

### Calculations

Since the program is based on relatively complex mathematical algorithms that are not necessarily self explanatory, I will give a brief overview of how each component is being simulated. The two separate simulations, for flight and motor, are listed separately.

### Flight Simulation

I am using an Euler approximation to solve the differential equations, which may mean that the time increment must be small before it is accurate. The simulation has five degrees of freedom, which means that it calculates motion in the x, y, and z coordinates as well as the yaw and pitch of the rocket (roll is not calculated). Also, the rocket always has one angle of attack because it is assumed to be a rigid body (I still need to add in some bending moment calculations).

#### Thrust

Right now, I am assuming that thrust always acts directly through the center of gravity (it causes no rotation; thus there is no propulsive restoring moment), and that it doesn't affect drag (no CD - Power On or CD - Power Off). There is no implementation for thrust vectoring / gimballing. However, the base motor class does have a few scaling factors, which should be implemented in all of the subclasses and allow you to arbitrarily scale up the burn time or the thrust output. The profile is currently a scaled up version of (this motor)[https://www.thrustcurve.org/simfiles/5f4294d20002e900000004d1/], but I would like to replace it with my own simulation eventually.

#### Gravitational Pull

I am using the equation for gravitational attraction between two bodies, `weight = G * m * m / distance ^ 2`. The weight always acts in the negative z direction.

#### Drag and Lift

I use drag force, the air resistance provided in the direction of free-stream relative velocity, rather than the axial force that rocket simulations usually have. It provides some of the restoring force that acts on the fins to bring realignment.

I also use lift force, the component of air resistance perpendicular to drag (as opposed to normal force, which is perpendicular to the rocket). I am assuming that all lift and drag forces are being applied at the center of pressure - I am pretty sure that is correct.

Drag and lift forces are usually expressed in terms of an area-coefficient term multiplying the dynamic pressure on the rocket. I am currently retrieving my drag and lift coefficients from RASAero, but I would really like to get some CFD based calculations going.

#### Torque

Torque is the way forces transform energy into angular velocity. It is dependent on the distance between the point the force is acting on (usually CP) and the point that the object rotates about (always CG). For a more detailed look into the specifics of the trigonometry that guides how the forces are translated into torque, there is something of an explanation in the comments of the `apply_torque` function of the `Rocket` class.

Also, for some reason I really struggled with this initially: forces that cause rotation also cause the same amount of translational impact as they would have if the object was fixed. Think about how the particles all move when one of them is pushed really hard. They should have the same average momentum.

#### Center of Gravity

Everything on the rocket that has mass inherits from the `MassObject` class. The class provides an easy way to calculate the moment of inertia ([using a discretized form of the definition integral](https://www.thoughtco.com/moment-of-inertia-formulas-2698806)) with a CG property and a mass property, and I think it works relatively well as a subclass through the front distance property.

It's worth providing a side note about hybrid rockets here: on the solid rockets used by most amateurs, the CG only moves forwards through the burn. However, as the ox tank unloads, it often moves backwards in a hybrid. Hence, all of the simulations for dynamic stability.

#### Center of Pressure

The center of pressure is determined from RASAero, and is a property of the overall rocket class. I would like to provide a custom implementation of this (probably based on some extension of the Barrowman equations) at some point.

#### Wind Simulation

For some reason, research on high-fidelity (second-by-second) wind simulations appears to be practically non-existent on the internet. If anyone is aware of a technique to generate continuous wind data at high frequencies, I would love to see it. At the moment, I have a fake simulation based on some extrapolation from a few articles that I read.

The general idea is that wind speeds follow a Weibull distribution. Using perlin noise simulations averaged 30 times I can obtain a rolling series of numbers with a normal distribution (by the central limit theorem), which can be mapped to a weibull distribution. I am missing one very important parameter: time compression/dilation. I don't know what scale the perlin noise should be at, and I haven't found any sources that I could match this to. Also, this is all conjecture and could be totally wrong.

I plan to implement some wind simulations based on a table of wind data from White Sands shortly.

#### Notation of Implementation

I use coordinates x, y, and z in that order, with indicating the vertical axis. Angles are defined in radians in terms of a rotation around the vertical axis, starting from facing the positive x-axis, and a rotation down from the vertical, basically around the perpendicular of the object. It may be easier to think of the two angles as a rotation down around the y-axis followed by a rotation around the z-axis. These angles don't correspond particularly well with yaw and torque because they are not relative to the way the rocket faces initially.

### Motor Simulation

Everything in the motor is based off of Paraffin and Nitrous without any pressurant (though it should be easy to add). Again, I am using the explicit (https://en.wikipedia.org/wiki/Explicit_and_implicit_methods) Euler approximation to solve each time step.

#### Ox Tank

The ox tank is simulated using fitted properties from http://edge.rit.edu/edge/P07106/public/Nox.pdf. The calculations assume the tank is adiabatic and there is thermodynamic equilibrium between the gas and liquid. As I understand it, this should give a good lower bound for pressure, thus a lower bound for ox mass flow. You can read more about how I implemented it in [this Google doc](https://docs.google.com/document/d/1wdYWqgM0Wl63pFUSrCRhfAZ8hQWpamdUno7EoJ8Q770/edit?usp=sharing).

#### Injector

Because Nitrous is an extremely volatile liquid, the calculations performed by the injector must model two-phase flow - the equilibrium of liquid and gas through a small orifice. I plan to eventually implement a calculation proposed by Dyer based on experiments on the Peregrine rocket, in which the mass flow rate is determined by an interpolation between single phase flow and complete phase equilibrium (also assuming thermodynamic equilibrium and equal velocity between the gas and liquid phase).

#### Combustion Chamber

The combustion chamber only calculates the evolution of conditions within the space. It does not account for the effects of pre or post combustion spaces in anything other than volume. It uses the conservation of mass and assumes the ideal gas law in order to model the pressure over time (you can read through the derivation of the equation [here](https://www.overleaf.com/read/fphwwxgjvqbf)), storing the relevant information in pressure, volume, and density variables (notice that we do not need to include moles or mass within the chamber, the information is implicit and can be calculated from what we do store). Most of the combustion characteristics are taken from CEA, and the temperature in the combustion chamber is assumed to reach the combustion flame temperature instantly.

DISCLAIMER: Right now the combustion chamber pressure over time is not correct at all.

##### Fuel Grain

Since the fuel grain is housed in the combustion chamber, it is basically a child object of the combustion chamber in the code. At the moment, I have only implemented the highly-empirical, space-averaged equation that has grown out of Marxman's original research (`r-dot = a * G_ox ** n`), with coefficients collected from https://stacks.stanford.edu/file/druid:ng346xh6244/BenjaminWaxmanFinal-augmented.pdf, but you can probably find equally good numbers from other (much shorter) sources.

#### Nozzle

The code for the nozzle assumes completely isentropic flow that is always choked at the throat. It does account for differences between the exit pressure and the atmospheric pressure, but it will never warn you if the flow detaches.

#### Notation and Units

There are many terms to represent the ratio of specific heats for a fluid (notably gamma, γ, isentropic coefficient, isentropic exponent, k, κ, and probably some others), I have chosen to use isentropic_exponent consistently, for no particular reason.

All temperatures are in Kelvin, I try to keep to the metric system (going so far as to use base Pascals), and I use radiuses in meters.

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

Merge this random git branch with a ton of changes (and actually start making sure that the main banch can run everythin)
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