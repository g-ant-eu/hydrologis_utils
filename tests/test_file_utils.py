from hydrologis_utils.file_utils import *

import unittest

# run with python3 -m unittest discover tests/


class TestStrings(unittest.TestCase):
    def test_folder_removal(self):
        structure = {
            "mainfolder1": {
                "subfolder11": ["file111.txt", "file112.txt"],
                "subfolder12": ["file121.csv", "file122.csv"],
                "subfolder13": {
                    "subsubfolder131": ["file1311.txt"],
                    "subsubfolder132": [],
                },
                "file1.txt": {"type": "file"},
            },
            "mainfolder2": {
                "subfolder21": ["file211.txt"],
                "file2.csv": {"type": "file"},
            },
        }

        folder = create_tmp_folder()
        print(type(folder))
        print(folder)
        # create_file_structure(folder, structure)




if __name__ == "__main__":
    unittest.main()
