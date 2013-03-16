
class Star:
    def __init__(self, id, name, ra, dec, mag):
        self.id = id
        self.name = name
        self.ra = ra
        self.dec = dec
        self.mag = mag

    def __str__(self):
        return "<%s.Star(%s, %s, %s, %s, %s)>" % (__name__, self.id, self.name, self.ra, self.dec, self.mag)


class Line:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def __str(self):
        return "<%s.Line(%s, %s)>" % (__name__, self.point1, self.point2)