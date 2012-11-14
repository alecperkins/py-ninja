from decimal        import Decimal
from exceptions     import ValueError
import colorsys


class Temperature(object):
    """
    A class for working with temperatures. It provides helpers for converting
    between Kelvin, Celsius, Fahrenheit, and Rankine. Internally, the
    temperature is stored as Kelvin in a Decimal. All of the conversions are
    returned in Decimal form, for the sake of .

    Access each conversion by using the corresponding attribute:

        >>> t = Temperature(1.0)
        >>> t
        Temperature(1)
        >>> t.k
        Decimal('1')
        >>> t.c
        Decimal('-272.15')
        >>> t.f
        Decimal('-457.870')
        >>> t.r
        Decimal('1.80')
        >>> str(t)
        '1 K'

    Temperatures can be generally treated like a number, using various
    operators like <, >, +, -, *. If operating on two Temperatures, their
    Kelvin value will be used.

        >>> t1 = Temperature(k=40)
        >>> t2 = Temperature(f=212)
        >>> t2 - t1
        Temperature(333.15)
        >>> (t2 - t1).f
        Decimal('140.000')
        >>> t1 * 2
        Temperature(80)

    To operate on a temperature without creating another Temperature instance,
    simply operate on the unit attribute, and the other operand will be used as
    that unit:

        >>> t = Temperature(0)
        >>> t.f += 100
        >>> t
        Temperature(55.5556)

    If the specified temperature is less than 0 Kelvin, a `ValueError` will be
    raised.

        >>> t = Temperature(-5)
        [...traceback omitted...]
        Exception: Temperature Kelvin value (-4) cannot be less than 0
        >>> t1 = Temperature(100)
        >>> t2 = Temperature(200)
        >>> t1 - t2
        [...traceback omitted...]
        Exception: Temperature Kelvin value (-4) cannot be less than 0


    Derived from http://code.activestate.com/recipes/286226-temperature-class/
    with some operadtor overloading and sanity checks (eg prevent temperatures
    less than 0 K).
    """

    equations = {
        'c': ( Decimal('1.0'), Decimal('0.0')     , Decimal('-273.15') ),
        'f': ( Decimal('1.8'), Decimal('-273.15') , Decimal('32.0') ),
        'r': ( Decimal('1.8'), Decimal('0.0')     , Decimal('0.0') ),
    }

    def __init__(self, k=0.0, **kwargs):
        self.k = k
        for key in kwargs:
            if key in ('c', 'f', 'r'):
                setattr(self, key, kwargs[key])
                break

    def __getattr__(self, name):
        if name in self.equations:
            eq = self.equations[name]
            return (self.k + eq[1]) * eq[0] + eq[2]
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        value = Decimal(value)
        if name in self.equations:
            eq = self.equations[name]
            self.k = (value - eq[2]) / eq[0] - eq[1]
        else:
            object.__setattr__(self, name, value)
        if self.k < 0:
            k = self.k
            self.k = 0
            raise ValueError('Temperature Kelvin value (%s) cannot be less than 0' % (k,))



    def __str__(self):
        return "%g K" % self.k

    def __repr__(self):
        return "Temperature(%g)" % self.k

    def __lt__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return self.k < other
    
    def __le__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return self.k <= other
    
    def __gt__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return self.k > other
    
    def __ge__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return self.k >= other
    
    def __eq__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return self.k == other
    
    def __ne__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return self.k != other
    
    def __add__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return Temperature(self.k + other)
    
    def __sub__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return Temperature(self.k - other)
    
    def __mul__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return Temperature(self.k * other)
    
    def __div__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        return Temperature(self.k / other)

    def __iadd__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        self.k = self.k + other
        return self
    
    def __isub__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        self.k = self.k - other
        return self
    
    def __imul__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        self.k = self.k * other
        return self
    
    def __idiv__(self, other):
        if hasattr(other, 'k'):
            other = other.k
        self.k = self.k / other
        return self

    def __int__(self):
        return int(self.k)

    def __long__(self):
        return long(self.k)

    def __float__(self):
        return float(self.k)

    def __complex__(self):
        return complex(self.k)

    def __oct__(self):
        return oct(self.k)

    def __hex__(self):
        return hex(self.k)


def _passThrough(*args):
    return args

def _RGBToHex(r, g, b):
    data = []
    for d in [r, g, b]:
        d = hex(d).split('x')[1].upper()
        if len(d) < 2:
            d = '0' + d
        data.append(d)
    return ''.join(data)

def _hexToRGB(hex_str):
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return (r, g, b)

class Color(object):

    def __init__(self, *args):
        if len(args) == 1:
            if hasattr(args[0], 'split'):
                value = args[0].split(',')
                if len(value) == 3:
                    r, g, b = args[0].split(',')
                else:
                    r, g, b = _hexToRGB(value[0])
            else:
                r, g, b = args[0]
            r = int(r)
            g = int(g)
            b = int(b)
        elif len(args) == 3:
            r = args[0]
            g = args[1]
            b = args[2]
        else:
            r = 0
            g = 0
            b = 0
        self.r = r
        self.g = g
        self.b = b

    _converters = {
        'hls': (colorsys.rgb_to_hls, colorsys.hls_to_rgb),
        'rgb': (_passThrough, _passThrough),
        'hex': (_RGBToHex, _hexToRGB),
    }

    def __getattr__(self, name):
        if name in self._converters:
            return self._converters[name][0](self.r, self.g, self.b)
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in self._converters:
            self.r, self.g, self.b = self._converters[1](value)
        else:
            object.__setattr__(self, name, value)

    def __repr__(self):
        return 'Color%s' % (self.rgb,)

    def __str__(self):
        return ','.join([str(v) for v in self.rgb])

    def __iter__(self):
        return self.rgb.__iter__()

    def __len__(self):
        return len(self.rgb)

    def __contains__(self, v):
        return v in self.rgb

    def __getitem__(self, v):
        return self.rgb[v]

    @classmethod
    def _add_color_constant(cls, name, val):
        val = cls(val)
        setattr(cls, name, val)

_color_constants = {
    'WHITE'   : ( 255 , 255 , 255 ),
    'RED'     : ( 255 , 0   , 0   ),
    'GREEN'   : ( 0   , 255 , 0   ),
    'BLUE'    : ( 0   , 0   , 255 ),
    'CYAN'    : ( 0   , 255 , 255 ),
    'YELLOW'  : ( 255 , 0   , 255 ),
    'PURPLE'  : ( 255 , 255 , 0   ),
    'BLACK'   : ( 0   , 0   , 0   ),
}

for name, rgb in _color_constants.items():
    Color._add_color_constant(name, rgb)
