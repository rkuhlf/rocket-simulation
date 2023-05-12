# Instead of using a table to look up the CP value, these equations are designed to calculate how much every component on a rocket contributes to the CP.
# However, they are not used anywhere, since it was too much work to change them all.

import numpy as np


def trapezoid_center_of_pressure(h, a, b, dist):
    # Note that b must be longer

    area = h * (a + b) / 2

    dist_from_base = h / 3 * (2 * a + b) / (a + b)
    dist += dist_from_base

    return area, area * dist


def triangle_center_of_pressure(p1, p2_p3, diff_2_3):
    """Center of pressure for a right triangle
    p1 is the distance from the nose of the rocket to one point on the triangle
    p2_p3 is the distance from the nose of the rocket to two points on the triangle
    diff_2_3 is the distance between points 2 and 3
    """

    # centroid is the sum of all y coordinates over 3
    area = 1 / 2 * (p1 - p2_p3) * diff_2_3

    dist = (p1 + 2 * p2_p3) / 3

    return area, area * dist


def rectangle_center_of_pressure(p1, p2, width):
    area = abs(p2 - p1) * width

    dist = (p1 + p2) / 2

    return area, area * dist


# Multiply each section of area of the rocket by the average distance from the nose of that area
# Then divided by the total area at the end
def cutout_method_of_CP(p, R, XP, LN, d, dF, LT, dR, XB, CR, XR, S, CT):
    # basically assumes that dF is the widest point of the rocket
    numerator = 0
    denominator = 0

    # Ogive
    # https://www.desmos.com/calculator/nykoxlqt4f
    # R is radius of ogive
    # p is radius of the circle it is cut from. It is actually a rho, but who cares
    o = p - R
    L = (p ** 2 - o ** 2) ** (1 / 2)

    area_dist = (-2 * (p ** 2 - L ** 2) **
                 (3 / 2) - 3 * o * L ** 2) / 6 + 64 / 3
    area = (p ** 2 * np.arcsin(L / p) + p * L * (1 - L **
                                                 2 / p ** 2) ** (1 / 2)) / 2 + o * L

    numerator += area_dist
    denominator += area

    # Wide body
    area, area_dist = trapezoid_center_of_pressure(XP - LN, d, dF, LN)

    numerator += area_dist
    denominator += area

    # transition
    area, area_dist = trapezoid_center_of_pressure(LT, dR, dF, XP)
    numerator += area_dist
    denominator += area

    # Narrow body
    height = XB + CR - (LT + XP)
    area, area_dist = trapezoid_center_of_pressure(height, dR, R, XP + LT)

    numerator += area_dist
    denominator += area


    # Fins
    # The cross sectional area of the rocket depends on the roll. Sort of. It depends on the roll and also the angle of attack, because that is what determines what the cross section of the fins looks like. For now, we will go with two, full, trapezoidal fins. This is optimistic, making the sim less likely to fail
    # Because the trapezoids have a different orientation, I'm doing it with separate triangles
    area, area_dist = triangle_center_of_pressure(XB, XB + XR, XR)
    numerator += area_dist
    denominator += area

    area, area_dist = rectangle_center_of_pressure(XB + XR, XB + CR, S)
    numerator += area_dist
    denominator += area

    area, area_dist = triangle_center_of_pressure(
        XB + CR, XB + XR + CT, XR + CT - CR)
    numerator += area_dist
    denominator += area


    return numerator / denominator



# Barrowman equations assume straight up flight, circular symmetry, and 3 or 4 fins. Also assumes some stuff about nosecone
# Barrowman equation basically breaks rocket down into sections, then adds up the individual CPs
# Comes from https://www.apogeerockets.com/downloads/PDFs/barrowman_report.pdf


def barrowman_equation(
        LN, d, dF, dR, LT, XP, CR, CT, S, LF, R, XR, XB, N=3, is_ogive=True):
    """Determines the constant center of pressure at a zero angle of attack given lots of information about the shape of the rocket
    LN	=	length of nose
    d	=	diameter at base of nose
    dF	=	diameter at front of transition
    dR	=	diameter at rear of transition
    LT	=	length of transition
    XP	=	distance from tip of nose to front of transition
    CR	=	fin root chord
    CT	=	fin tip chord
    S	=	fin semispan
    LF	=	length of fin mid-chord line
    R	=	radius of body at aft end
    XR	=	distance between fin root leading edge and fin tip leading edge parallel to body
    XB	=	distance from nose tip to fin root chord leading edge
    N	=	number of fins
    """

    # http://www.rocketmime.com/rockets/Barrowman.html

    # TODO: Figure out what this equation means and what the letters stand for

    # Nose Cone Terms
    CNN = 2
    XN = (0.666 if is_ogive else 0.466) * LN

    # Conical transition terms
    CNT = 2 * ((dR / d) ** 2 - (dF / d) ** 2)

    XT = XP + LT / 3 * (1 + (1 - dF / dR) / (1 - dF / dR) ** 2)

    # Fin Terms
    CNF = (1 + R / S + R) * 4 * N * (S / d) ** 2 / (1 +
                                                    (1 + (2 * L / (CR + CT)) ** 2) ** (1 / 2))

    XF = XB + XR / 3 * (CR + 2 * CT) / (CR + CT) + 1 / \
        6 * ((CR + CT) - CR * CT / (CR + CT))

    # Final calculation
    CNR = CNT + CNF + CNN

    center_of_pressure = (CNN * XN + CNT * XT + CNF * XF) / CNR


    return center_of_pressure


# Comes from http://ftp.demec.ufpr.br/foguete/bibliografia/Labudde_1999_CP.pdf
# incorporates high angle of attack situations
# This is basically just interpolating by sine
# This one is for CP. There should also be one for coefficient of drag, but I think I will have to simulate that one in CFD
def extended_barrowman_equation(
        mach, angle_of_attack, center_of_pressure_at_zero,
        perpendicular_center_of_pressure):
    body_center_of_pressure = center_of_pressure_at_zero + np.sin(abs(
        angle_of_attack)) * (perpendicular_center_of_pressure - body_center_of_pressure)

    return body_center_of_pressure


# http://ftp.demec.ufpr.br/foguete/bibliografia/Labudde_1999_CP.pdf
def stall_angle(span, AF):
    """
    AF is the lateral area of the fins
    Span is the length from the fin root to the fin tip. It is the widest point
    """
    AR = span ** 2 / AF
    a = 15 * (1 + 1.1 / AR)

    return a
