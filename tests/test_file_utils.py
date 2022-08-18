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

    def test_file_utils(self):
        path = "/home/hydrologis/tmp/file.txt"
        self.assertEquals(get_file_name(path), "file.txt")
        self.assertEquals(get_file_name(path, remove_ext=True), "file")


        path1 = "/home/hydrologis"
        path2 = "tmp/"
        path3 = "file.txt"
        joined = join_paths(join_paths(path1, path2), path3)
        self.assertEquals(joined, "/home/hydrologis/tmp/file.txt")

    def test_zip_utils(self):
        tmp_folder = create_tmp_folder()
        f1 = join_paths(tmp_folder, "file1.txt")
        write_text_to_file(f1, "blah1")
        f2 = join_paths(tmp_folder, "file2.txt")
        write_text_to_file(f2, "blah2")
        outZip = join_paths(tmp_folder, "output.zip")

        list = [f1, f2]
        zip_files_list(list, outZip, use_basenames=True)
        
        self.assertTrue(os.path.exists(outZip))

        names = get_zip_file_names(outZip)
        self.assertEquals(len(names), 2)
        self.assertTrue("file1.txt" in names)
        self.assertTrue("file2.txt" in names)

    def test_file_list(self):
        tmp_folder = create_tmp_folder()
        f1 = join_paths(tmp_folder, "file1.csv")
        write_text_to_file(f1, "blah1")
        f2 = join_paths(tmp_folder, "file2.txt")
        write_text_to_file(f2, "blah2")

        list = list_files(tmp_folder)
        self.assertEquals(len(list), 2)
        list = list_files(tmp_folder, extension="csv")
        self.assertEquals(len(list), 1)


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
