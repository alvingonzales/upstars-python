


# hash structure:
# zoom - 8 bits
#     minimum zoom - 2
#     max zoom - 9

MIN_ZOOM = 2
MAX_ZOOM = 9


ZOOM_BITS = (MAX_ZOOM - MIN_ZOOM).bit_length()
SCALAR_BITS = (2**MAX_ZOOM - 1).bit_length()

def to_hash(zoom, x, y):
    if zoom < MIN_ZOOM or zoom > MAX_ZOOM:
        raise Exception("Zoom out of range")

    max_scalar = 2**zoom - 1
    if x > max_scalar or y > max_scalar:
        raise Exception("Coordinates out of range")

    hash = (
        (zoom - MIN_ZOOM)
        | (x << ZOOM_BITS)
        | (y << (ZOOM_BITS + SCALAR_BITS))
    )

    return hash

def to_coords(hash):
    zoom = (hash & (2**ZOOM_BITS - 1)) + MIN_ZOOM
    x = (hash >> ZOOM_BITS) & (2**SCALAR_BITS - 1)
    y = hash >> (ZOOM_BITS + SCALAR_BITS)

    return zoom, x, y

for z in range(2, 10):
    for x in range(2**z):
        for y in range(2**z):
            assert(to_coords(to_hash(z, x, y)) == (z, x, y))