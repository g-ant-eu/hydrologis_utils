from sqlalchemy import null
from hydrologis_utils.color_utils import *

import unittest

# run with python3 -m unittest discover tests/

class TestColorUtils(unittest.TestCase):
    
    def test_existence(self):
        colorNames = [e.value for e in ColorTableNames]
        for name in colorNames:
            self.assertTrue(name in COLORTABLES)

    def test_next_value(self):
        ctName = ColorTableNames.RAINBOW.value

        cprov = ColorProvider(ctName)
        ct = COLORTABLES[ctName]
        
        for i in range(6):
            c1 = cprov.get_next_hex_color()
            c2 = ct[i]
            self.assertEqual(c1, c2)
        
        for i in range(6):
            c1 = cprov.get_next_hex_color()
            c2 = ct[i]
            self.assertEqual(c1, c2)
    
    def test_list(self):
        ctName = ColorTableNames.RAINBOW.value

        cprov = ColorProvider(ctName)
        ct = COLORTABLES[ctName]

        colors = cprov.get_hex_color_list(3)
        
        for i in range(3):
            c1 = colors[i]
            c2 = ct[i]
            self.assertEqual(c1, c2)



if __name__ == "__main__":
    unittest.main()