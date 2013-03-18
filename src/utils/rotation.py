from math import pi, sin, cos, acos, asin, floor, sqrt, atan, atan2
from utils.vectors import V as Vector, M as Matrix


def azalt_to_vector(az, alt):
    az = az*pi/12
    alt = alt*pi/180

    alt = alt + pi/2
    # computing against unit circle (r=1)
    r = 1.0
    x = r * sin(alt) * cos(az)
    y = r * sin(alt) * sin(az)
    z = r * cos(alt)

    return Vector(x, y, z)


def vector_to_azalt(v):
    x, y, z = v
    r = sqrt(x**2 + y**2 + z**2)
    az = atan2(y, x)
    alt = acos(z/r)
    alt = alt - pi/2
    # hours and degrees
    az = az*12/pi
    alt = alt*180/pi

    if az < 0:
        az = az + 24

    return round(az, 5), round(alt, 5)


def rotate_azalt(az, alt, az_d, alt_d):
    v = azalt_to_vector(az, alt)
    az_d = az_d * pi/12.0
    alt_d = alt_d * pi/180.0

    if az_d:
        q = Matrix.rotate("Z", az_d)
        v = q*v
    if alt_d:
        q = Matrix.rotate("Y", alt_d)
        v = q*v

    v = Vector(v[0], v[1], v[2])

    return vector_to_azalt(v)


def main():
    for az in range(1, 25):
        for alt in range(-89, 89):
            original = (az, alt)
            v = azalt_to_vector(*original)
            print "v", v
            azalt = vector_to_azalt(v)
            assert azalt == original, (azalt, original)


if __name__ == "__main__":
    main()
