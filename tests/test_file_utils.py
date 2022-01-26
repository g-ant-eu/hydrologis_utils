from hydrologis_utils.file_utils import *

import unittest

# run with python3 -m unittest discover tests/


class TestFileUtils(unittest.TestCase):
    def test_file_io(self):
        tmp_file = create_tmp_file()
        path = tmp_file.name
        tmp_file.close()
            
        text = """line1
        line2
        line3"""

        write_text_to_file(path, text)
        new_text = read_text_from_file(path)
        self.assertEquals(text, new_text)

        lines = ["line1","line2","line3"]
        write_list_to_file(path, lines)
        newLines = read_text_lines_from_file(path)
        self.assertEquals(lines, newLines)

        data = [
            ["1", "2"],
            ["3", "4"],
        ]
        write_list_to_csv(path, data)
        csv_lines = read_text_lines_from_file(path)
        self.assertEquals(csv_lines[0], "1;2")
        self.assertEquals(csv_lines[1], "3;4")

        data = [
            {
                "id": "1",
                "name": "test1",
                "cat": "cat1"
            },
            {
                "id": "2",
                "name": "test2",
                "cat": "cat2"
            },
            {
                "id": "3",
                "cat": "cat3"
            }
        ]
        write_dict_to_csv(path, ["id", "name", "cat"], data)
        csv_lines = read_text_lines_from_file(path)
        self.assertEquals(csv_lines[0], "id;name;cat")
        self.assertEquals(csv_lines[1], "1;test1;cat1")
        self.assertEquals(csv_lines[2], "2;test2;cat2")
        self.assertEquals(csv_lines[3], "3;;cat3")



    # def test_folder_removal(self):
    #     structure = {
    #         "mainfolder1": {
    #             "subfolder11": ["file111.txt", "file112.txt"],
    #             "subfolder12": ["file121.csv", "file122.csv"],
    #             "subfolder13": {
    #                 "subsubfolder131": ["file1311.txt"],
    #                 "subsubfolder132": [],
    #             },
    #             "file1.txt": {"type": "file"},
    #         },
    #         "mainfolder2": {
    #             "subfolder21": ["file211.txt"],
    #             "file2.csv": {"type": "file"},
    #         },
    #     }

    #     folder = create_tmp_folder()
    #     print(type(folder))
    #     print(folder)
        ## create_file_structure(folder, structure)




if __name__ == "__main__":
    unittest.main()
