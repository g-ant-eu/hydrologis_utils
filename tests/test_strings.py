from hydrologis_utils.strings.utils import check_same_name, split_string

import unittest

class TestStrings(unittest.TestCase):
    
    def test_checkname(self):
        string = "name"

        strings = ["name"]
        checked = check_same_name(strings, string)

        self.assertEqual(checked, "name (1)", "Should be: name (1)")
    
    def test_split_string(self):
        string = "Sit deserunt aliquid magni aspernatur laboriosam. Itaque itaque fugiat aut odit aut nulla voluptas ipsa. Aperiam ut odit eius amet nesciunt corrupti. Commodi hic corporis et omnis."
        list = split_string(string, 20)
        print(list)

if __name__ == "__main__":
    unittest.main()