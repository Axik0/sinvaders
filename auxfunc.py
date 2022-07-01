import math as m


def trajectory_calc(point, angle_deg):
    """I take coordinates and angle (degrees) and generate an equation for the line collinear to this vector"""
    x0, y0 = point[0], point[1]
    angle = m.radians(angle_deg)
    slope = m.tan(angle)
    intercept = y0 - slope * x0
    # return slope, intercept
    return -slope, 1, -intercept


def line_intersection(line1, line2):
    """each line is a tuple of 3 parameters for ax+by+c=0 equation on 2D-surface.
    I suppose that neither a1 nor b1 are zero for line1 could be y=kx+b.
    For the line2, a2 and b2 can't be zeros simultaneously.
    With that in assumption, I proceed with calculation of the point of their intersection."""
    a1, b1, c1 = line1[0], line1[1], line1[2]
    k, d = -a1 / b1, -c1 / b1
    a2, b2, c2 = line2[0], line2[1], line2[2]
    xi = - (b2 * d + c2) / (b2 * k + a2)
    yi = (a2 * d - c2 * k) / (b2 * k + a2)
    return xi, yi


def reflex(angle_deg, line):
    """this function returns an angle of vector's (given by angle) reflection over some line"""
    # note that resulting angle is an acute one, -90..+90
    angle_line = m.atan(m.radians(angle_deg))
    return angle_line - angle_deg


def hor(angle_deg):
    # this rotation = ball reflects over a horizontal line
    return -angle_deg


def ver(angle_deg):
    # this rotation = ball reflects over a vertical line
    return 180-angle_deg