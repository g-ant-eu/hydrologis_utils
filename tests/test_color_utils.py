from sqlalchemy import null
import sys
sys.path.append("./")
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
            c1 = cprov.getNextHexColor()
            c2 = ct[i]
            self.assertEqual(c1, c2)
        
        for i in range(6):
            c1 = cprov.getNextHexColor()
            c2 = ct[i]
            self.assertEqual(c1, c2)
    
    def test_list(self):
        ctName = ColorTableNames.RAINBOW.value

        cprov = ColorProvider(ctName)
        ct = COLORTABLES[ctName]

        colors = cprov.getHexColorList(3)
        
        for i in range(3):
            c1 = colors[i]
            c2 = ct[i]
            self.assertEqual(c1, c2)

    def test_darken(self):
        c = "#00FF00"
        results = [
            "#00ff00",
            "#00cc00",
            "#009900",
            "#006600",
            "#003300",
        ]

        for i in [0, 1,2,3,4]:
            darkC = ColorUtilities.getDarkerColor(c, offset=i*0.2)
            self.assertEqual(results[i], darkC)

    def test_birghten(self):
        c = "#003300"
        results = [
            "#003300",
            "#336633",
            "#669966",
            "#99cc99",
            "#ccffcc",
        ]

        for i in [0, 1,2,3,4]:
            brightC = ColorUtilities.getBrighterColor(c, offset=i*0.2)
            self.assertEqual(results[i], brightC)

    def test_colors(self):
        c = "#FF0000"
        hc = HyColor(hexColor=c)

        self.assertEqual(hc.getHex(), "#FF0000FF")
        self.assertEqual(hc.getRgba(), (255, 0, 0, 255))

        hc = HyColor(rgbaColor=(255, 0, 0, 0))
        self.assertEqual(hc.getHex(), "#FF000000")
        self.assertEqual(hc.getRgba(), (255, 0, 0, 0))



if __name__ == "__main__":
    unittest.main()