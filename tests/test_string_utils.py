from hydrologis_utils.string_utils import checkSameName, splitString, trimOrPadToCount

import unittest

# run with python3 -m unittest discover tests/

class TestStringUtils(unittest.TestCase):
    
    def test_checkname(self):
        string = "name"

        strings = ["name"]
        checked = checkSameName(strings, string)

        self.assertEqual(checked, "name (1)", "Should be: name (1)")
    
    def test_split_string(self):
        lim = 20
        string = "Sit deserunt aliquid magni aspernatur laboriosam. Itaque itaque fugiat aut odit aut nulla voluptas ipsa. Aperiam ut odit eius amet nesciunt corrupti. Commodi hic corporis et omnis."
        list = splitString(string, lim)
        self.assertEqual(list[0], "Sit deserunt aliquid")
        for l in list:
            self.assertLessEqual(len(l), lim)
    
    def test_trim_or_pad_to_count(self):
        string = "1234567890"
        count = 12
        new_string = trimOrPadToCount(string, count)
        self.assertEqual(new_string, "1234567890  ")
        
        count = 8
        new_string = trimOrPadToCount(string, count)
        self.assertEqual(new_string, "12345678")
        
            

if __name__ == "__main__":
    unittest.main()