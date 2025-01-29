from hydrologis_utils.file_utils import *

import unittest

# run with python3 -m unittest discover tests/


class TestFileUtils(unittest.TestCase):
    def test_file_io(self):
        path = createTmpFile()

            
        text = """line1
        line2
        line3"""

        writeTextToFile(path, text)
        
        self.assertTrue(exists(path))

        new_text = readTextFromFile(path)
        self.assertEqual(text, new_text)

        lines = ["line1","line2","line3"]
        writeListToFile(path, lines)
        newLines = readTextLinesFromFile(path)
        self.assertEqual(lines, newLines)

        data = [
            ["1", "2"],
            ["3", "4"],
        ]
        writeListToCsv(path, data)
        csv_lines = readTextLinesFromFile(path)
        self.assertEqual(csv_lines[0], "1;2")
        self.assertEqual(csv_lines[1], "3;4")

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
        writeDictToCsv(path, data, header=["id", "name", "cat"])
        csv_lines = readTextLinesFromFile(path)
        self.assertEqual(csv_lines[0], "id;name;cat")
        self.assertEqual(csv_lines[1], "1;test1;cat1")
        self.assertEqual(csv_lines[2], "2;test2;cat2")
        self.assertEqual(csv_lines[3], "3;;cat3")

        writeDictToCsv(path, data)
        csv_lines = readTextLinesFromFile(path)
        self.assertEqual(csv_lines[0], "id;name;cat")
        self.assertEqual(csv_lines[1], "1;test1;cat1")
        self.assertEqual(csv_lines[2], "2;test2;cat2")
        self.assertEqual(csv_lines[3], "3;;cat3")

    def test_file_utils(self):
        path = "/home/hydrologis/tmp/file.txt"
        self.assertEqual(getFileName(path), "file.txt")
        self.assertEqual(getFileName(path, remove_ext=True), "file")


        path1 = "/home/hydrologis"
        path2 = "tmp/"
        path3 = "file.txt"
        joined = joinPaths(joinPaths(path1, path2), path3)
        self.assertEqual(joined, "/home/hydrologis/tmp/file.txt")

    def test_zip_utils(self):
        tmp_folder = createTmpFolder()
        f1 = joinPaths(tmp_folder, "file1.txt")
        writeTextToFile(f1, "blah1")
        f2 = joinPaths(tmp_folder, "file2.txt")
        writeTextToFile(f2, "blah2")
        outZip = joinPaths(tmp_folder, "output.zip")

        list = [f1, f2]
        zipFilesList(list, outZip, use_basenames=True)
        
        self.assertTrue(os.path.exists(outZip))

        names = getZipFileNames(outZip)
        self.assertEqual(len(names), 2)
        self.assertTrue("file1.txt" in names)
        self.assertTrue("file2.txt" in names)

    def test_file_list(self):
        tmp_folder = createTmpFolder()
        f1 = joinPaths(tmp_folder, "file1.csv")
        writeTextToFile(f1, "blah1")
        f2 = joinPaths(tmp_folder, "file2.txt")
        writeTextToFile(f2, "blah2")

        list = listFiles(tmp_folder)
        self.assertEqual(len(list), 2)
        list = listFiles(tmp_folder, extension="csv")
        self.assertEqual(len(list), 1)


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
