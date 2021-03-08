import numpy as np


def save_line(variable, variables, target):
    current_value = variables[variable]
    if type(current_value) is np.ndarray:
        assignment = "np.array(%s, dtype='%s')" % (
            str(list(current_value)),
            current_value.dtype.name)
    else:
        assignment = str(current_value)

    target.write(variable + " = " + assignment + "\n")




initial_orientation_names = ['position',
                             'velocity', 'rotation', 'angular_velocity']

rocket_features = ['radius', 'height',
                   'center_of_gravity', 'center_of_pressure', 'mass']

rocket_drag = [
    'drag_coefficient', 'drag_coefficient_perpendicular', 'vertical_area',
    'sideways_area']

misc_names = ['base_altitude']


def write_section(title, names, variables, target):
    target.write("\n\n# %s\n" % title)
    for name in names:
        save_line(name, variables, target)


def save_preset(name, variables):
    f = open('Data/Input/Presets/' + name + '.py', 'w')

    f.write("import numpy as np\n")

    write_section('Orientation', initial_orientation_names, variables, f)
    write_section('Rocket Features', rocket_features, variables, f)
    write_section('Drag', rocket_drag, variables, f)
    write_section('Miscellaneous', misc_names, variables, f)

    f.close()
