from lib.general import linear_intersection, interpolate_point, transpose_tuple
import matplotlib.pyplot as plt
import numpy as np

def calculate_nozzle_coordinates_bezier(initial_point, initial_angle, final_point, final_angle, divisions=100):
    """
        Return a series of x, y coordinate pairs that make up a quadratic Bezier.
        Supposedly, this curve is an approximation for the Method of Characteristics.
        Angles should be in radians
    """

    initial_slope = np.tan(initial_angle)
    final_slope = np.tan(final_angle)
    
    intersection_point = linear_intersection(initial_point, initial_slope, final_point, final_slope)

    points = []

    for i in range(divisions):
        start_point = interpolate_point(i, 0, divisions - 1, initial_point, intersection_point)
        end_point = interpolate_point(i, 0, divisions - 1, intersection_point, final_point)

        points.append(interpolate_point(i, 0, divisions - 1, start_point, end_point))

    return points


def calculate_nozzle_coordinates_truncated_parabola(initial_point, initial_angle, final_point, divisions=100):
    # Calculate the extrapolated vertex point
    # Print the length fraction based on the passed final point

    # Assuming x^2 parabola

    initial_slope = np.tan(initial_angle)

    x1, y1 = initial_point
    x2, y2 = final_point

    numerator = y2 - y1 - initial_slope * x2 + initial_slope * x1
    denominator = x2 ** 2 - 2 * x1 * x2 - x1 ** 2 + 2 * x1 ** 2

    a = numerator / denominator
    b = initial_slope - 2 * a * x1
    c = y1 - a * x1 ** 2 - b * x1

    nozzle_height = lambda x : a * x ** 2 + b * x + c
    angle = lambda x : 2 * a * x + b

    print(f"The exit angle for the truncated bell is {angle(final_point[0])} radians \
            or {angle(final_point[0]) * 180 / np.pi} degrees")

    inputs = np.linspace(initial_point[0], final_point[0], divisions)
    outputs = nozzle_height(inputs)


    points = [inputs, outputs]

    # Convert tuples to 2d numpy
    # https://stackoverflow.com/questions/39806259/convert-list-of-list-of-tuples-into-2d-numpy-array
    points = np.array([*points])
    points = points.transpose()

    return points

#endregion

#region FUNCTIONS TO BE RUN FOR DISPLAY
def display_constructed_quadratic():
    start_point = (0, 0.1)
    start_angle = 35 / 180 * np.pi

    end_point = (1, 0.5)
    end_angle = 8 / 180 * np.pi

    points = calculate_nozzle_coordinates_bezier(start_point, start_angle, end_point, end_angle)

    # Convert tuples to 2d numpy - https://stackoverflow.com/questions/39806259/convert-list-of-list-of-tuples-into-2d-numpy-array
    points = np.array([*points])
    points = points.transpose()

    plt.plot(points[0], points[1])
    inputs = np.linspace(start_point[0], end_point[0])
    plt.plot(inputs, np.tan(start_angle) * (inputs - start_point[0]) + start_point[1])
    plt.plot(inputs, np.tan(end_angle) * (inputs - end_point[0]) + end_point[1])
    plt.show()


def compare_truncated_to_quadratic():
    start_point = (0, 0.1)
    start_angle = 35 / 180 * np.pi

    end_point = (1, 0.5)
    end_angle = 5.717686887804168 / 180 * np.pi

    quadratic_points_nonzero = transpose_tuple(calculate_nozzle_coordinates_bezier(start_point, start_angle, end_point, end_angle))
    quadratic_points_zero = transpose_tuple(calculate_nozzle_coordinates_bezier(start_point, start_angle, end_point, 0))
    truncated_points = transpose_tuple(calculate_nozzle_coordinates_truncated_parabola(start_point, start_angle, end_point))

    fig, ((ax1, hide_me_1), (ax2, hide_me_2)) = plt.subplots(2, 2)

    ax1.plot(quadratic_points_nonzero[0], quadratic_points_nonzero[1])
    ax1.plot(truncated_points[0], truncated_points[1])
    ax1.set(title="Same Angle", xlabel="Horizontal Distance", ylabel="Horizontal Distance")

    ax2.plot(quadratic_points_zero[0], quadratic_points_zero[1])
    ax2.plot(truncated_points[0], truncated_points[1])
    ax2.set(title="Different Angle", xlabel="Horizontal Distance", ylabel="Horizontal Distance")

    hide_me_1.axis('off')
    hide_me_2.axis('off')

    # So, my implementation of the parabolic nozzle construction is slightly different from Cristian's. In his model, the component that is allowed to vary is the length, rather than the exit angle
    # I believe that the first one matched up simply by chance, but I am pretty sure that the quadratic bezier solution is slightly more general.
    # However, the parabolic construction may be the method that 80%-bell is referring to.
    hide_me_1.text(-0.1, 0, "When the exit angles are equivalent, the \nnozzles appear to be an exact match. \nThe quadratic bezier adds another degree \nof freedom, allowing you to vary the exit \nangle. From Rao's original publications, \nthe exit angle is an important factor \nin properly approximating the shape.")

    plt.show()



if __name__ == "__main__":
    # display_constructed_quadratic()
    # calculate_nozzle_coordinates_truncated_parabola((0, 0.1), 35 * np.pi / 180, (1, 0.5))
    # compare_truncated_to_quadratic()

    pass