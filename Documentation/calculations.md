# Calculations

Simulating a rocket requires many equations, and there are often multiple options for which ones to implement. The most important calculations should be documented here.

## Inputs

### Coefficient of Drag

A DIY simulation of CD is very unpractical. It would require an entire meshing algorithm, full implementation of the Navier-Stokes equations and turbulence modelling, not to mention the mathematical know-how involved in simultaneously solving the PDEs. Therefore, the main goal is to be able to get the data from some kind of CFD.

I know that Autodesk (they make Fusion 360) is supposed to have some kind of CFD software, but I don't know how to use it and it seems like it would be difficult to add onto a Python project. The ultimate goal is to provide an stl file and have an OpenFoam setup automatically generated which simulates all angles and speeds. Unfortunately, it turns out CFD is very finicky, and it would be very difficult to create a sim like that. As it is, I thought it was best to keep CD determination completely separate. 

P.S. OpenFoam was really hard for me to learn and you might want to go for some kind of GUI-based CFD.

### Wind
It turns out that simulating wind accurately is very difficult and not that important to how a rocket flies. I hope to get a working method to generate wind that is consistent with Lake Jackson's terrain, the altitude the rocket is at, and the time. It should be relatively continuous, but the amount of wind data is really lacking

#### Weibull Distribution
Apparently, wind speeds generally follow approximately a Weibull distribution. I don't know how wind changes over time to do that. I really need a Weibull perlin noise distribution.

A Weibull noise distribution could potentially be made by taking a bunch of Gaussian noise, then transforming each of the numbers so that it goes from the normal value to the weibull value.

As for standard deviation randomness, basically you just need all of the values under the curve to sum to one.

The only issue is that perlin noise isn't actually normally distributed. I don't know how it is distributed and you would probably have to come up with your own distribution depending on the number of octaves there are. You could use CLT. If you have thirty separate perlin noise functions, their average value should follow a normal distribution. You just have to figure out the standard deviation, then you can figure out the z-score of each one, which will tell you the percentile.

The noise value goes from 0 to 1 and it tells you what percentile it is in. The weibull value should also go from 0 to 1. From that perlin noise generation, you get the percentile you want. Then you look it up in the weibull lookup chart.

<!-- Maybe worth making a note of, but this is just rude; it really belongs in a different file besides. Generate 4D noise. Nope. You can't just have each of the three axes generated individually. You have to generate the strength and the angle, otherwise all three will add up to a different magnitude than you expect -->

#### Altitude
There is a function that gives the average wind speed at any altitude based on the wind speed at a certain point and the terrain roughness there. That should be enough to make a continuous thing.

#### Direction
I guess I should just have the average be multiplied by some random direction. I don't think there is ever much vertical wind.

### Models
Most matematical models will be quicker to calculate tan a lookup, so it is sometimes worth mapping some kind of function to your data points. 

#### Numpy Polynomial vs lmfit
TL;DR: lmfit is better. Though most of the other code is written using numpy for calculations, the polynomial class is very poorly supported. There are basically two versions, and looking through the documentation for either one is a nightmare. It is also hard to save the model.

lmfit is built entirely for this kind of thing - fitting a user-inputted function to input-output data. Eventually, everything should be generated using lmfit.


## Inaccuracies in Inputs
Most rocket simulation software only allows you to input one possible value for each input. However, aerodynamics is a particularly inaccurate science, with difficulties determining coefficients of force to even one significant figure. Therefore, I thought it would be useful to allow inputs that covered a range of data. To do so, I think it makes the most since to have custom override functions for each class.

Simply allow the user to input an array of two items, worst-case first followed by best-case. The program would then run two simulations and output the range of possible outcomes. 

An even more advanced version of this software could accept an array of objects - value-probability pairs - and create a sampling distribution from that. It would take a weighted random value from each object, then run the simulation, appending the result to a collection of results. A a relatively continuous graph of the results could then be created

## Nomenclature
I call the rotational moment torque, but it isn't really torque. Torque as units Newton-meters, but I am using a force with radians per second^2 kilograms - The main difference is that I don't have the extra meters in it. Actually I'm not sure there's a difference.

I tried to capitalize python files that are intended to be run. For the most part, files that begin with a lowercase are just helpers.


## Rotation
It holds all of the information about the rocket's shape. Then I can put some of the barrowman stuff in there
It also throws you a message if the engine wouldn't fit

Using rotation around, rotation down. Later I will add roll, but I think the effects are too complicated atm
Using global rotation, not relative rotation based on the rocket
When rotation is zero (measured in radians), the rocket is headed straight up
It's against safety procedures to launch at an angle more than 30 degrees from vertical
Unless there is wind, rotation around (index zero) should not change at all; That part is working correctly

## Parachute Deployment
The 2020-2021 Goddard team used a linear increase in the radius



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
