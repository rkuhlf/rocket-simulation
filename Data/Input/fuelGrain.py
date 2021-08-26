# Generate input-output data for the 2D cross-section surface area of the fuel grain given a base shape and the regression rate

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

# I think it should be pretty flat on all of the sides, so push all of the pixels up one i and down one i, then chop off that top pointy bit


# The interior will be white, or 1, and the exterior will be black, or 0
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

    pixel_mask = np.ndarray((pixels.shape[:2]))

    ox_mask = np.where((pixels[:, :, 0] == 255) & (pixels[:, :, 1] == 255))
    # fuel_mask = np.where((pixels[:, :, 0] == 0) & (pixels[:, :, 1] == 0))
    wall_mask = np.where((pixels[:, :, 0] == 255) & (pixels[:, :, 1] == 0))


    pixel_mask[ox_mask[0], ox_mask[1]] = 1
    pixel_mask[wall_mask[0], wall_mask[1]] = -1
    # They are automatically initialized to zero
    # pixel_mask[fuel_mask[0], fuel_mask[1]] = 0

    return pixel_mask


def display_image(array):
    pixels = np.ndarray((array.shape[0], array.shape[1], 3))
    debug_mask = np.where((array == 2))
    ox_mask = np.where((array == 1))
    fuel_mask = np.where((array == 0))
    wall_mask = np.where((array == -1))

    pixels[debug_mask[0], debug_mask[1]] = [255, 0, 0]
    pixels[ox_mask[0], ox_mask[1]] = [255, 255, 255]
    pixels[wall_mask[0], wall_mask[1]] = [255, 0, 255]
    pixels[fuel_mask[0], fuel_mask[1]] = [0, 0, 0]

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

    possible_edges = []

    for edge_index in edges:
        base_i, base_j = edge_index
        # Determine which pixels are within a circle of the pixel by looping through all of the pixels less than ... away
        i_offset = int(round(distance))
        min_i = base_i - i_offset
        max_i = base_i + i_offset

        for i in range(min_i, max_i + 1):
            j_offset = int(
                round((distance ** 2 - (i - base_i) ** 2) ** (1 / 2)))
            min_j = base_j - j_offset
            max_j = base_j + j_offset

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

                    if i == min_i or i == max_i:
                        print("appendin")
                    possible_edges.append((i, j))


                # Loop through all of the possible edge pixels, checking if that pixel is an edge
                # Loop through the edge pixels and determine their distance

    return possible_edges





if __name__ == "__main__":
    pixels = load_image("Data/Input/grainCrossSectionColored.png")

    # Take the pixelated image. Determine all of the edge pixels (diagonals only)
    edges = []

    # It's okay to do this over all of the pixels just the one time, but the repeated algorithm needs to be faster
    for i in range(len(pixels)):
        for j in range(len(pixels[0])):
            if is_ox_edge(i, j, pixels):
                edges.append((i, j))


    possible_edges = regress_fuel_grain(10, pixels, [(100, 400)])

    for index in possible_edges:
        pixels[index[0], index[1]] = 2

    # print(possible_edges)


    display_image(pixels)





# Other possible approaches:

# I can see the vague outlines of something linear algebra based in my head
# Multiply each pixel by an edge detector
# Multiply each pixel by a circle matrix to see if it is close enough
# If I can get the distance calculation vectorized, that way will be faster than this
