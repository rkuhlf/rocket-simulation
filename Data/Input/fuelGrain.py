# Generate input-output data for the 2D cross-section surface area of the fuel grain given a base shape and the regression rate

# SOURCES OF ERROR:
# It is not totally accurate to represent curved shapes with pixels. I thought this error would go away as pixels -> infinity, but it did not. The error appears to flatten out at about 5% overestimation for a circle, but that number will obviously vary with different shapes

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

# I think it should be pretty flat on all of the sides, so push all of the pixels up one i and down one i, then chop off that top pointy bit


# The interior (oxidizer) will be white, or 1, and the exterior will be black, or 0
# The walls of a combustion chamber will be represented by a -1. The color to match is that N/A magenta
def load_image(path):
    """
    Transform the color data from a supplied path into number data that can be read by the simulation.
    Pure magenta (FF00FF) is a wall
    Black (000000) is fuel grain
    White (FFFFFF) is oxidizer

    Returns a numpy array of the pixels, access with [x, y]
    """

    im = Image.open(path)  # Can be many different formats.

    pixels = np.asarray(im).copy()

    pixel_mask = np.ndarray((pixels.shape[:2]), dtype=int)

    ox_mask = np.where((pixels[:, :, 0] == 255) & (pixels[:, :, 1] == 255))
    fuel_mask = np.where((pixels[:, :, 0] == 0) & (pixels[:, :, 1] == 0))
    wall_mask = np.where((pixels[:, :, 0] == 255) & (pixels[:, :, 1] == 0))


    pixel_mask[ox_mask[0], ox_mask[1]] = 1
    pixel_mask[wall_mask[0], wall_mask[1]] = -1
    # They are automatically initialized to zero
    pixel_mask[fuel_mask[0], fuel_mask[1]] = 0

    return pixel_mask


def create_image(array):
    pixels = np.ndarray((array.shape[0], array.shape[1], 3))
    debug_mask = np.where((array == 2))
    ox_mask = np.where((array == 1))
    fuel_mask = np.where((array == 0))
    wall_mask = np.where((array == -1))

    pixels[debug_mask[0], debug_mask[1]] = np.asarray([1, 0, 0])
    pixels[ox_mask[0], ox_mask[1]] = np.asarray([1, 1, 1])
    pixels[wall_mask[0], wall_mask[1]] = np.asarray([1, 0, 1])
    pixels[fuel_mask[0], fuel_mask[1]] = np.asarray([0, 0, 0])

    return pixels


def save_image(name, array):
    img = create_image(array)
    plt.imsave(name, img, format="PNG")


def display_image(array):
    pixels = create_image(array)

    # For some reason PIL freaks out if you try and get it to show the pixels
    plt.imshow(pixels, interpolation='nearest')
    plt.show()



# The best, most efficient way to do this, is to compose the grain shape of lines determined mathematically (svg), then extend them by their normal values

# The way discussed in https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=2378&context=etd&httpsredir=1&referer= is to blur a pixelated image of the grain, then delete all of the pixels that aren't fully black.

# There is definitely a much better way to do this, which I implement here

# Take the pixelated image. Determine all of the edge pixels (diagonals only)
# Determine which pixels are within a circle of the pixel by looping through all of the pixels less than ... away
# TODO: Figure out this equation, I think you can do it with sine and cosine
# Add the first and last x of every loop to the new possible edge pixels (only if it changes the color of the pixel)
# Loop through all of the possible edge pixels, checking if that pixel is an edge

# If there is a black pixel adjacent (not diagonal) to the pixel to check, it is an edge
def is_edge(i, j, image):
    """
    Checks if any adjacent pixels are black
    Assumes the pixel being check is white
    """
    if i != len(image) - 1 and image[i + 1][j] == 0:
        return True

    if i != 0 and image[i - 1][j] == 0:
        return True

    if j != len(image[0]) - 1 and image[i][j + 1] == 0:
        return True

    if j != 0 and image[i][j - 1] == 0:
        return True

    return False


def is_adjacent(a, b):
    """
    Accepts two tuples of indices, returns whether they are off by one
    """

    if a[0] == b[0]:
        if a[1] == b[1] + 1 or a[1] == b[1] - 1:
            return True
    elif a[1] == b[1]:
        if a[0] == b[0] + 1 or a[0] == b[0] - 1:
            return True

    return False


def is_diagonal(a, b):
    x_off = a[0] - b[0]
    y_off = a[1] - b[1]

    return abs(x_off) == 1 and abs(y_off) == 1


def is_diagonal_without_fuel(a, b, image):
    if not is_diagonal(a, b):
        return False

    # check if the cells in between are oxidizer (they should be for it to be diagonal)
    if image[a[0], b[1]] == 1 or image[b[0], a[1]] == 1:
        return True

    return False


def is_ox_edge(i, j, image):
    return image[i, j] == 1 and is_edge(i, j, image)


def get_edges(possible_indices, image):
    edges = []
    for possible_index in possible_indices:
        i, j = possible_index
        if is_edge(i, j, pixels):
            edges.append((i, j))

    return edges


def regress_fuel_grain(distance, image, edges):
    """
    Move the fuel grain back from the normal by a given distance (in pixels)
    The distance can be calculated by regression rate * time
    Returns the new image and the new possible edges
    """

    distance += 0.5

    possible_edges = []

    for edge_index in edges:
        base_i, base_j = edge_index
        # Determine which pixels are within a circle of the pixel by looping through all of the pixels less than ... away
        i_offset = int(np.floor(distance))
        min_i = base_i - i_offset
        max_i = base_i + i_offset

        for i in range(min_i, max_i + 1):
            j_offset = int(
                np.floor(((distance ** 2 - (i - base_i) ** 2) ** (1 / 2))))
            min_j = base_j - j_offset
            max_j = base_j + j_offset

            # Not working right now because there is an edge pixel I'm not including

            # Need a special case for min and max because that is where the edge of the circle is
            # This is where meta programming would be better because I could insert it into the loop and it would be equally fast
            if image[i, min_j] == 0:
                image[i, min_j] = 1
                possible_edges.append((i, min_j))

            # Add the first and last x of every loop to the new possible edge pixels (only if it changes the color of the pixel)

            if image[i, max_j] == 0:
                image[i, max_j] = 1
                possible_edges.append((i, max_j))

            # There is no minus one on max_j because it is automatically exclusive
            for j in range(min_j + 1, max_j):
                if image[i, j] == 0:
                    image[i, j] = 1

                    # I tink tis simple ceck makes it faster
                    if i == min_i or i == max_i:
                        possible_edges.append((i, j))
                    elif np.sqrt((i - base_i) ** 2 + (j - base_j) ** 2) > (distance - 1):
                        possible_edges.append((i, j))


    return possible_edges


# FIXME: For some reason this somewhat (5%) overestimates the total edge distance of a large circle
# It doesn't overestimate the small circle by as much
# I would think it would get more accurate as the circle gets bigger
# I think that makes sense, as the number of pixels increases though it should improve
def get_edge_distance(edges, pixels):
    "From an unordered list of edges in 2D, calculate the path between them"
    # I think maybe te easiest to do is to steal the algorithm from a machine learning
    # https://docs.opencv.org/3.3.1/d4/d73/tutorial_py_contours_begin.html
    # Matlab bwboundaries

    # Actually, I should probably make my own algorithm because those will not use the known edges
    edges = edges.copy()

    distance = 0  # in pixels

    adjacent_distance = 1
    diagonal_distance = np.sqrt(2)

    # Start at edge index 0 (this is basically random)
    current_edge = edges[0]
    current_index = 0

    # While there are still edges
    while (len(edges) > 0):
        connected = None
        to_add = 0
        for edge, index in zip(edges, range(len(edges))):

            # Check if any of the edges are adjacently connected to the active edge
            if is_adjacent(edge, current_edge):
                # to_add the distance depending on whether it is adjacent or diagonal
                to_add = adjacent_distance
                connected = edge
                connected_index = index
                pixels[edge[0], edge[1]] = 2
                break
            # Check if any of the edges are diagonally connected to the active (there cannot be any fuel grain in between them)
            elif is_diagonal_without_fuel(edge, current_edge, pixels):
                to_add = diagonal_distance
                connected = edge
                connected_index = index
                break


        # Set the current edge to the newly found edge. Delete the old edge
        if connected is not None:
            distance += to_add
            try:
                del edges[current_index]
                current_edge = connected
            except:
                break

            # If we just deleted an index beneath it, you need to decrement the index we will use next by one
            if current_index < connected_index:
                connected_index -= 1

            current_index = connected_index
        else:
            # If there are no connected edges, delete the edge, add no distance, and set the new current_edge to the index zero
            del edges[current_index]
            try:
                current_edge = edges[0]
                current_index = 0
            except:
                break

    return distance


# TODO: further testing required for internal circle
# Gear demonstrates issues best
if __name__ == "__main__":
    base_path = "Data/Input/RegressionImages/"
    file_name = "gear.png"
    pixels = load_image(base_path + file_name)

    # Take the pixelated image. Determine all of the edge pixels (directly adjacent to fuel only, should generate a diagonal line)
    edges = []

    # It's okay to do this over all of the pixels just the one time, but the repeated algorithm needs to be faster
    for i in range(len(pixels)):
        for j in range(len(pixels[0])):
            if is_ox_edge(i, j, pixels):
                edges.append((i, j))


    r = 0
    total_regression = 50
    iters = 15
    interp_increment = total_regression / iters
    regressions = []
    areas = []



    # Generate data
    for _ in range(iters):

        possible_edges = regress_fuel_grain(interp_increment, pixels, edges)
        save_image(base_path + file_name + "Regressed" + str(r) + ".png", pixels)

        # Loop through all of the possible edge pixels, checking if that pixel is an edge
        edges = get_edges(possible_edges, pixels)

        # Loop through the edge pixels and determine their distance
        linear_surface_area = get_edge_distance(edges, pixels)


        regressions.append(r)
        areas.append(linear_surface_area)

        r += interp_increment





    print(regressions, areas)
    plt.plot(regressions, areas)
    plt.show()

    # linear_surface_area = get_edge_distance(edges, pixels)
    # print(linear_surface_area)

    # display_image(pixels)




# Other possible approaches:

# I can see the vague outlines of something linear algebra based in my head
# Multiply each pixel by an edge detector
# Multiply each pixel by a circle matrix to see if it is close enough
# If I can get the distance calculation vectorized, that way will be faster than this
