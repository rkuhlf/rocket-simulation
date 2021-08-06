Potential Issues:
- Translational drag isn't opposed to rotation correctly
- The calculation for angular drag is wrong
- Something, somewhere is seeking the vertical axis instead of the direction of motion
    - The gravity-pressure thing is flipped somewhere
    - If it only has a z-axis drag effect, it will seek the center



# Design Notes

Since the project is sort of sprawling and might be a little confusing, particularly coming from an excel based math model, I thought I would provide some reasoning behind some of the design decisions.

The rocket model system makes fairly consistent use of object oriented design throughout. By separating each main component of the simulation into its own class, files can be made smaller and it is easier to figure out where things belong. The rocket is in a section all by itself, where it basically performs all of the necessary aerodynamics calculations. Because there are way more factors affecting aerodynamics than anything else, it takes up way more space than anything else. The parachute and motor classes are separate, but it simplifies where data is stored a little bit. Object-oriented structure also lends itself to a component based rocket simulation. You can change which motor you want to use, but keep the same rocket frame. In case I ever want to rewrite the aerodynamics stuff, I kept the simulation and logging apart from the rocket itself.

Unfortunately, every decision has its downsides, and a class-based system generates lots of different files and sometimes wastes time. For example, it is difficult to efficiently fit a model for drag, then copy that model over to the models section, then copy a call to that model over to the environment. However, I couldn't really figure out a better way to do it.

Helpers is supposed to have general 'helper' functions, which aren't specific to rockets or to aerodynamics, but accept arguments and return a solution. The functions should have descriptive names so that you don't have to go into the folder to figure out what they do.

There are some folders that I mostly just kept so that all of the stuff would be in one place. Tests is just to make sure some of the tricky calculations are working correctly, but it isn't really finished. Visualization is to help figure out what is wrong with the rocket, but also to make sure that things are working correctly.

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

Generate 4D noise. Nope. You can't just have each of the three axes generated individually. You have to generate the strength and the angle, otherwise all three will add up to a different magnitude than you expect

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
Most rocket simulation software only allows you to input one possible value for each input. However, aerodynamics is a particularly inaccurate science, with difficulties determining coefficients of force to even one significant figure. Therefore, I thought it would be useful to allow inputs that covered a range of data. To do so, I think it makes the most since to extend the simulation class. <!-- TODO: do this. It might take quite a bit of finagling, and multiple rocket objects might have to be created -->

Simply allow the user to input an array of two items, worst-case first followed by best-case. The program would then run two simulations and output the range of possible outcomes. 

An even more advanced version of this software could accept an array of objects - value-probability pairs - and create a sampling distribution from that. It would take a weighted random value from each object, then run the simulation, appending the result to a collection of results. A a relatively continuous graph of the results could then be created