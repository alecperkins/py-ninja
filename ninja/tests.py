import unittest

class Test_Temperature(unittest.TestCase):

    def setUp(self):
        from .units import Temperature
        from decimal import Decimal
        self.Decimal = Decimal
        self.Temperature = Temperature

        self.temp100 = Temperature(100)

    def testUnits(self):
        self.assertEqual(self.temp100.k, self.Decimal('100'))
        self.assertEqual(self.temp100.c, self.Decimal('-173.15'))
        self.assertEqual(self.temp100.f, self.Decimal('-279.670'))
        self.assertEqual(self.temp100.r, self.Decimal('180.00'))

    def testOperators(self):
        self.temp100 += 100
        self.assertEqual(self.temp100.k, self.Decimal('200'))
        self.temp100 -= 100
        self.assertEqual(self.temp100.k, self.Decimal('100'))
        t = self.temp100 + 100
        self.assertEqual(t.k, self.Decimal('200'))
        t = self.temp100 - 100
        self.assertEqual(t.k, self.Decimal('0'))
        t = self.temp100 * 4
        self.assertEqual(t.k, self.Decimal('400'))
        t = self.temp100 / 4
        self.assertEqual(t.k, self.Decimal('25'))
        t = self.temp100 * self.Temperature(4)
        self.assertEqual(t.k, self.Decimal('400'))
        t = self.temp100 / self.Temperature(4)
        self.assertEqual(t.k, self.Decimal('25'))

    def testSubZero(self):
        self.assertRaises(ValueError, self.Temperature, -100)



class Test_NinjaAPI(unittest.TestCase):
    def setUp(self):
        from .api import NinjaAPI
        self.NinjaAPI = NinjaAPI

    def testRequireAccessToken(self):
        self.assertRaises(ValueError, self.NinjaAPI)
        self.assertRaises(ValueError, self.NinjaAPI, 1, 2, 3)


