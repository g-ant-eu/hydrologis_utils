"""
Utilities to work with files.
"""

import os
import shutil
import tempfile
import csv
import zipfile

def getHome():
    """
    Get the home of the current user.
    """
    return os.path.expanduser('~')

def exists(path):
    """
    Check if a file exists in the given path.
    """
    return os.path.exists(path)

def createTmpFile(mode = "w+"):
    """Create a temp file path.

    The file path will not yet exist when returning from this method.

    :param mode: the file mode to use.
    :return: the temp file path.
    """
    f = tempfile.NamedTemporaryFile(mode = mode)
    path = f.name
    f.close()
    return path

def createTmpFolder():
    """Create a temp folder.

    :return: the created folder path.
    """
    path = tempfile.mkdtemp()
    return path

def createFolder(path):
    """Create a folder.
    
    :param  path: the path to create the folder with.
    """
    os.makedirs(path)

def deleteFolder(folder_path):
    """Delete a folder and its content.
    """
    shutil.rmtree(folder_path)

def joinPaths(path1, path2):
    """Joint parts of a paths.
    
    :param path1: the first path piece.
    :param path2: the second path piece.
    :return: the joined path.
    """
    return os.path.join(path1, path2)

def copyFile( fromPath, toPath ):
    """Copy a file from one path to another.

    :param fromPath: the path to the file to copy.
    :param toPath: the path for the new file.
    """
    shutil.copyfile(fromPath, toPath)

def getFileName(path, remove_ext=False):
    """
    Get the file name from a path.
    
    Parameters
    ----------
    path: String
        The file path.
    remove_ext: boolean
        If True, remove the extension from the name.
    
    Returns
    -------
    string:
        the file name.
    """

    basename = os.path.basename(path)
    if remove_ext:
       basename = os.path.splitext(basename)[0]
    return basename


def getModificationTimestamp(path):
    """Get the modification timestamp of an existing file.

    :param path: the path to the file to check.
    :return: the timestamp (unix epoch) of last modification.
    """
    return os.path.getmtime(path)


def deleteFileOrFolder(path):
    """Delete a file or a folder and its content.

    :param path: the path to the file/folder to remove.
    """
    if os.path.isfile(path) or os.path.islink(path):
        os.unlink(path)
        return

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def writeListToFile(path, lines_list, append=False):
    """Write a list of lines to a file.

    :param path: the absolute path to write to.
    :param lines_list: a list of lists of the data to write to file.
    :param append: optional parameter to append to an existing file.
    """
    mode = 'a' if append else 'w'
    with open(path, mode) as out_file:
        is_first = True
        for line in lines_list:
            if not is_first:
                out_file.write('\n')
            else:
                is_first = False
            out_file.writelines(line)

def writeTextToFile(path, text, append=False):
    """Write text to a file.

    :param path: the absolute path to write to.
    :param text: a text to write to file.
    :param append: optional parameter to append to an existing file.
    """
    mode = 'a' if append else 'w'
    with open(path, mode) as out_file:
        out_file.write(text)

def readTextFromFile(path, encoding='UTF-8'):
    """Read text from a file.

    :param path: the absolute path to read from.
    :return: the read string.
    """
    
    with open(path, 'r', encoding=encoding) as out_file:
        return out_file.read()

def readTextLinesFromFile(path, encoding='UTF-8'):
    """Read text lines list from a file.

    :param path: the absolute path to read from.
    :return: the read lines list.
    """
    
    with open(path, 'r', encoding=encoding) as out_file:
        return out_file.read().split("\n")

def writeListToCsv(path, rows_list, delimiter=";", encoding='UTF-8'):
    """Write a list of rows to a csv file.

    :param path: the absolute path to write to.
    :param rows_list: a list of lists of the data to write to file.
    :param delimiter: optional delimiter.
    :param encoding: optional encoding.
    """
    with open(path,'w', encoding=encoding) as out_csv_file:
        csv_writer = csv.writer(out_csv_file, dialect=csv.excel, delimiter=delimiter)
        for row in rows_list:
            csv_writer.writerow(row)

def writeDictToCsv(path, dict_list, header=None, delimiter=";", encoding='UTF-8'):
    """Write a list of rows to a csv file.

    :param path: the absolute path to write to.
    :param dict_list: a list of dictionaries of the data to write to file.
    :param header: the csv fields. If not available, it is taken from the first dictionary.
    :param delimiter: optional delimiter.
    :param encoding: optional encoding.
    """
    with open(path,'w', encoding=encoding) as out_csv_file:
        if not header:
            header = [k for k,v in dict_list[0].items()]

        csv_writer = csv.DictWriter(out_csv_file, fieldnames=header, dialect=csv.excel, delimiter=delimiter)
        csv_writer.writeheader()
        for dict in dict_list:
            csv_writer.writerow(dict)

def zipFilesList(files_list, output_zip_file, use_basenames=True, remove_path_from_name=""):
    """
    Zip files from a list of paths.
    
    Parameters
    ----------
    files_list: list
        the list of files to zip.
    output_zip_file: path
        the zip file to create.
    use_basenames: boolean
        if True, use the basenames in the zip file (no full path).
    remove_path_from_name: string
        if not empty, remove the path from the basename (to create relative paths).
    """
    with zipfile.ZipFile(output_zip_file, 'w') as zipMe:        
        for file in files_list:
            basename = file
            if use_basenames:
                basename = os.path.basename(basename)
            if remove_path_from_name:
                basename = basename.replace(remove_path_from_name, "")
            zipMe.write(file, arcname=basename, compress_type=zipfile.ZIP_DEFLATED)

def getZipFileNames(zip_file):
    """
    Get th elist of files in a zip.
    
    Parameters
    ----------
    zip_file: string
        the zip file path.
    
    Returns
    -------
    list:
        the list of names of the items in the zip.
    """

    with zipfile.ZipFile(zip_file, 'r') as zip:
        return zip.namelist()

# def create_file_structure(basepath, structure):
#     """Create a files and folders structure from a dictionary.

#     :param basepath: the folder in which to create the structure.
#     :param structure: the dictionary containing the structure.
#     """

#     if not os.path.exists(basepath):
#         raise Exception("The base folder needs to exist.")
    
#     __walk_and_create_structure(structure)

# def __walk_and_create_structure(folder, structure):
#     for type, object in structure.items():
#         if type == "folder":
#             os.path.join(folder, object)

    
def listFiles(folder_path, extension=None):
    """
    List files inside a folder.
    
    Parameters
    ----------
    folder_path: str
        the folder to list files from.
    extenstion: str
        optiona extension to filter on.
    
    Returns
    -------
    list:
        the list of file names found in the folder.
    """
    list = []
    for name in os.listdir(folder_path):
        if extension and not name.endswith(extension):
            continue
        list.append(name)
    return list