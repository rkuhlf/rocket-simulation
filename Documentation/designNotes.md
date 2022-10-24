<!-- TODO: This stuff is really out of date and most of it needs to be re-written -->
<!-- Mention repeated use of get_sim -->
<!-- Mention getters and setters -->
<!-- Mention saving functionality -->
<!-- Mention the verbose = True thing -->

# Design Notes

Since the project is sort of sprawling and might be a little confusing, particularly coming from an excel based math model, I thought I would provide some reasoning behind some of the design decisions.

The rocket model system makes fairly consistent use of object oriented design throughout. By separating each main component of the simulation into its own class, files can be made smaller and it is easier to figure out where things belong. The rocket is in a section all by itself, where it basically performs all of the necessary aerodynamics calculations. Because there are way more factors affecting aerodynamics than anything else, it takes up way more space than anything else. The parachute and motor classes are separate, but it simplifies where data is stored a little bit. Object-oriented structure also lends itself to a component based rocket simulation. You can change which motor you want to use, but keep the same rocket frame. In case I ever want to rewrite the aerodynamics stuff, I kept the simulation and logging apart from the rocket itself.

Unfortunately, every decision has its downsides, and a class-based system generates lots of different files and sometimes wastes time. For example, it is difficult to efficiently fit a model for drag, then copy that model over to the models section, then copy a call to that model over to the environment. However, I couldn't really figure out a better way to do it.

Helpers is supposed to have general 'helper' functions, which aren't specific to rockets or to aerodynamics, but accept arguments and return a solution. The functions should have descriptive names so that you don't have to go into the folder to figure out what they do.

There are some folders that I mostly just kept so that all of the stuff would be in one place. Tests is just to make sure some of the tricky calculations are working correctly, but it isn't really finished. Visualization is to help figure out what is wrong with the rocket, but also to make sure that things are working correctly.


In general, within the simulation folder, Optimize means that we have control over it, sensitivity to means we do not have control (but I still need to see the effect that using the wrong number will have).


I have tried to use object-oriented practices for all of the modelling. Each component from the fins to the body tube to the injector must be instantiated independently, then linked together by the rocket or motor class. For design, I went for a more functional approach. In my naming conventions, I have attempted to keep clear practices for determing the name of each function. Within a class, if a function returns a value, it should begin with *get_*, but if it has side effects it should be *calculate_*. For optimization design functions, the prefix is *determine_*, but for general purpose design functions and helper functions, you should use *find_*.

<!-- Move some of this kind of stuff to my personal notes on the Horizon 1 engineering process -->
I have tried to use the *if __name__ == "__main__" idiom wherever a file has code that is meant to be run. In addition, files that should be run begin with a capital letter, as well as all folder names.

There are many ways to program multiple objects so that they take data differently but perform the same calculations on it. At the moment, I am trying to have the main parent object for a class always accept a few different kinds of `set_` function, like `set_constant_mass` or `set_CG_function` or `set_thrust_table`. However, implementing these must always result in a change to the properties of the object, otherwise preset object will not be able to save it properly.

This readme file is really long, so I have more information about the design practices listed under a designNotes.md file.

### A Note on Preset Object

The idea is that eventually everything will be saveable. Also it allows the settings to be passed in as a config argument. I know there are other idioms like *kwargs that may be better suited for this, I might swap everything out later.

I think there is a half-finished attempt to implement something like that saving feature buried somewhere in here.



<!-- I have tried to put file paths that will usually need to be customized into a .env file. These will probably be different every time you clone the repository. -->