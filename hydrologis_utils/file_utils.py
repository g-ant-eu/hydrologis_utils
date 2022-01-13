"""
Utilities to work with files.
"""

import os
import shutil
import tempfile

def create_tmp_file(mode = "w+"):
    """Create a temp file, by default in text write mode.

    :param mode: the file mode to use.
    :return: the created file, which needs to be closed by the user.
    """
    f = tempfile.TemporaryFile(mode = mode)
    return f

def create_tmp_folder():
    """Create a temp folder.

    :return: the created folder.
    """
    f = tempfile.TemporaryDirectory()
    return f

def copy_file( fromPath, toPath ):
    """Copy a file from one path to another.

    :param fromPath: the path to the file to copy.
    :param toPath: the path for the new file.
    """
    shutil.copyfile(fromPath, toPath)


def get_modification_timestamp(path):
    """Get the modification timestamp of an existing file.

    :param path: the path to the file to check.
    :return: the timestamp (unix epoch) of last modification.
    """
    os.path.getmtime(path)


def delete_file_or_folder(path):
    """Delete a file or a folder and its content.

    :param path: the path to the file/folder to remove.
    """
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

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

    

