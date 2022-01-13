from sys import platform


def isLinux():
    return platform == "linux" or platform == "linux2"

def isWindows():
    return platform == "win32"

def isMacos():
    return platform == "darwin"
