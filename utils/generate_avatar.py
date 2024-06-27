import random

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImagePath

__all__ = ['render_identicon', 'IdenticonRendererBase']


class Matrix2D(list):
    """Matrix for Patch rotation"""

    def __init__(self, initial=None):
        if initial is None:
            initial = [0.] * 9
        assert isinstance(initial, list) and len(initial) == 9
        list.__init__(self, initial)

    def clear(self):
        for i in range(9):
            self[i] = 0.

    def set_identity(self):
        self.clear()
        for i in range(3):
            self[i] = 1.

    def __str__(self):
        return '[%s]' % ', '.join('%3.2f' % v for v in self)

    def __mul__(self, other):
        r = []
        if isinstance(other, Matrix2D):
            for y in range(3):
                for x in range(3):
                    v = 0.0
                    for i in range(3):
                        v += (self[i * 3 + x] * other[y * 3 + i])
                    r.append(v)
        else:
            raise NotImplementedError
        return Matrix2D(r)

    def for_PIL(self):
        return self[0:6]

    @classmethod
    def translate(cls, x, y):
        return cls([1.0, 0.0, float(x),
                    0.0, 1.0, float(y),
                    0.0, 0.0, 1.0])

    @classmethod
    def scale(cls, x, y):
        return cls([float(x), 0.0, 0.0,
                    0.0, float(y), 0.0,
                    0.0, 0.0, 1.0])

    @classmethod
    def rotateSquare(cls, theta, pivot=None):
        theta = theta % 4
        c = [1., 0., -1., 0.][theta]
        s = [0., 1., 0., -1.][theta]

        mat_r = cls([c, -s, 0., s, c, 0., 0., 0., 1.])
        if not pivot:
            return mat_r
        return cls.translate(-pivot[0], -pivot[1]) * mat_r * \
            cls.translate(*pivot)


class IdenticonRendererBase(object):
    PATH_SET = []

    def __init__(self, code):
        """
        @param code for icon
        """
        if not isinstance(code, int):
            code = int(code)
        self.code = code

    def render(self, size):
        """
        render identicon to PIL.Image

        @param size identicon patch size. (image size is 3 * [size])
        @return PIL.Image
        """

        # decode the code
        middle, corner, side, fore_color, back_color = self.decode(self.code)

        # make image
        image = Image.new("RGB", (size * 3, size * 3))
        draw = ImageDraw.Draw(image)

        # fill background
        draw.rectangle((0, 0, image.size[0], image.size[1]), fill=0)

        kwds = {
            'draw': draw,
            'size': size,
            'fore_color': fore_color,
            'back_color': back_color}
        # middle patch
        self.drawPatch((1, 1), middle[2], middle[1], middle[0], **kwds)

        # side patch
        kwds['type_'] = side[0]
        for i in range(4):
            pos = [(1, 0), (2, 1), (1, 2), (0, 1)][i]
            self.drawPatch(pos, side[2] + 1 + i, side[1], **kwds)

        # corner patch
        kwds['type_'] = corner[0]
        for i in range(4):
            pos = [(0, 0), (2, 0), (2, 2), (0, 2)][i]
            self.drawPatch(pos, corner[2] + 1 + i, corner[1], **kwds)

        return image

    def drawPatch(self, pos, turn, invert, type_, draw, size, fore_color,
                  back_color):
        path = self.PATH_SET[type_]
        if not path:
            # blank patch
            invert = not invert
            path = [(0., 0.), (1., 0.), (1., 1.), (0., 1.), (0., 0.)]
        patch = ImagePath.Path(path)
        if invert:
            fore_color, back_color = back_color, fore_color

        mat = Matrix2D.rotateSquare(turn, pivot=(0.5, 0.5)) * Matrix2D.translate(*pos) * Matrix2D.scale(size, size)

        patch.transform(mat.for_PIL())
        draw.rectangle((pos[0] * size, pos[1] * size, (pos[0] + 1) * size,
                        (pos[1] + 1) * size), fill=back_color)
        draw.polygon(patch, fill=fore_color, outline=fore_color)

    # virtual functions
    def decode(self, code):
        raise NotImplementedError


class DonRenderer(IdenticonRendererBase):
    """
    Don Park's implementation of identicon
    see : https://www.docuverse.com/blog/donpark/2007/01/19/identicon-updated-and-source-released
    """

    PATH_SET = [
        [(0, 0), (4, 0), (4, 4), (0, 4)],  # 0
        [(0, 0), (4, 0), (0, 4)],
        [(2, 0), (4, 4), (0, 4)],
        [(0, 0), (2, 0), (2, 4), (0, 4)],
        [(2, 0), (4, 2), (2, 4), (0, 2)],  # 4
        [(0, 0), (4, 2), (4, 4), (2, 4)],
        [(2, 0), (4, 4), (2, 4), (3, 2), (1, 2), (2, 4), (0, 4)],
        [(0, 0), (4, 2), (2, 4)],
        [(1, 1), (3, 1), (3, 3), (1, 3)],  # 8
        [(2, 0), (4, 0), (0, 4), (0, 2), (2, 2)],
        [(0, 0), (2, 0), (2, 2), (0, 2)],
        [(0, 2), (4, 2), (2, 4)],
        [(2, 2), (4, 4), (0, 4)],
        [(2, 0), (2, 2), (0, 2)],
        [(0, 0), (2, 0), (0, 2)],
        []]  # 15
    MIDDLE_PATCH_SET = [0, 4, 8, 15]

    # modify path set
    for idx in range(len(PATH_SET)):
        if PATH_SET[idx]:
            p = list(map(lambda vec: (vec[0] / 4.0, vec[1] / 4.0), PATH_SET[idx]))
            PATH_SET[idx] = p + p[:1]

    def decode(self, code):
        # decode the code
        middle_type = self.MIDDLE_PATCH_SET[code & 0x03]
        middle_invert = (code >> 2) & 0x01
        corner_type = (code >> 3) & 0x0F
        corner_invert = (code >> 7) & 0x01
        corner_turn = (code >> 8) & 0x03
        side_type = (code >> 10) & 0x0F
        side_invert = (code >> 14) & 0x01
        side_turn = (code >> 15) & 0x03
        blue = (code >> 16) & 0x1F
        green = (code >> 21) & 0x1F
        red = (code >> 27) & 0x1F

        fore_color = (red << 3, green << 3, blue << 3)

        return (middle_type, middle_invert, 0), \
            (corner_type, corner_invert, corner_turn), \
            (side_type, side_invert, side_turn), \
            fore_color, ImageColor.getrgb('white')


def render_identicon(name, renderer=None):
    size = 100
    code = random.randint(1, 100000000000)
    if not renderer:
        renderer = DonRenderer
    renderer(code).render(size).save(fp='tempFile/' + name)
