# GUI

McLeod seems to think it would be cool to have built our own simulation app. I agree.

## Things we can improve on other simulation apps
- I think that all of the current apps look really nasty. There are a lot of ways to build an interface for inputs, and I don't think that the options have been fully explored. I would love to try and build a screen-based app with very minimalistic interface
- **Custom motors**. I don't think that I've seen a custom motor easily accepted into another app.
    - Maybe openRocket allows you to create your own engine files?
    - Anyways, a thing that accepts motor inputs (dimensions and pressure and stuff) would be cool
- More options for simulating

## Options for Software
One of the main issues will probably be how to package the mathematics stuff with the GUI stuff. I don't know if I want to make a separate library that the GUI depends on (this seems like the best way), or to just keep building on top of this project and keep everything together (seems like it will spiral out of control).

I think that ultimately everything will be best-designed if it is a package. [How to Guide](https://packaging.python.org/tutorials/packaging-projects/)

### Requirements (In order of importance)
- Video playing: I think that eventually, it would be really cool to generate a custom video of the rocket flight
- Scrolling: One of the things that bothers me on the other rockets apps is the way that everything is so small. If we could just scroll a little bit it could make the UI much more modern
- Cross platform: It would be pretty nice to have it available online, but I think it should be first developed for desktop.

### Libraries
- tKinter: This is the default choice for GUI. I haven't really liked it when I used it in the past
    - After looking at some more of the code, I really don't like it. pack()? really? https://realpython.com/python-gui-tkinter/
- wxPython: Seems very well supported and has pretty reasonable programming style. https://zetcode.com/wxpython/skeletons/
    - No web support whatsoever 
    - I prefer the .setForegroundColor to tKinter's parameters
- flexx: I would really like to learn this one and I already have some experience working with the web-based rendering that it uses. I am slightly concerned about how the calculations would be implemented for this. Meh, I think I don't think I can choose this one due to some issues with development and documentation
    - It has about 75 downloads a day. That is not a lot. wxPython and pyside are both in the thousands
    - I actually really don't like the syntax and it looks like it doesn't really have many parallels with HTML & CSS. https://flexx.readthedocs.io/en/stable/examples/app_layout_src.html#app-layout-py
    - Also it has barely made it out of development and I don't know how much development is being done atm.