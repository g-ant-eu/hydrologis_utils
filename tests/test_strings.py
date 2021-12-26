from hydrologis_utils.strings.utils import check_same_name

import unittest

class TestStrings(unittest.TestCase):
    
    def test_checkname(self):
        string = "name"

        strings = ["name"]
        checked = check_same_name(strings, string)

        self.assertEqual(checked, "name (1)", "Should be: name (1)")



if __name__ == "__main__":
    unittest.main()