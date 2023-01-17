"""
Utilities to work with strings.
"""


def checkSameName( strings, checkString ):
    """Check if a string exists in a list of string and if necessary add a number to avoid collision.

    This is usefull for example when files shouldn't be overwritten.

    Parameters
    --------------
    :param strings : str[]
        a list of strings to check against.
    :param checkString : str
        the proposed new string, to be changed if colliding.

    :return: The modified string if collision was detected, the original string otherwise.
    """
    index = 0
    for string in strings:
        if index == 10000:
            raise Exception("Saving user assuming that 10000 files have not been created.")
        
        checkString = checkString.strip();
        if checkString == string.strip():
            # name exists, change the name of the entering
            index = index + 1
            if string.endswith(")"):
                string = string.strip().sub(r"([0-9]+)$", f"({index})", 1)
            else:    
                string = f"{string} ({index})"
            
            # start again
            i = 0
    
    return string
    

def splitString( string,  limit ):
    """Splits a string by char limit, not breaking works.
     
    :param string: the string to split.
    :param limit: the char limit.
    :return: the list of split words.
    """
    list = []

    # chars = string.toCharArray();
    endOfString = False
    start = 0
    end = start
    l = len(string)
    while start < l - 1:
        charCount = 0
        lastSpace = 0
        while charCount <= limit:
            if string[charCount + start] == ' ':
                lastSpace = charCount
            
            charCount = charCount + 1
            if charCount + start == l:
                endOfString = True
                break
            
        end = l if endOfString else lastSpace + start if (lastSpace > 0) else charCount + start
        sub = string[start:end]
        list.append(sub)
        start = end + 1
    return list

def trimOrPadToCount( string, count ):
    """Trims or pads a string to a given count.

    :param string: the string to trim or pad.
    :param count: the count to use.
    :return: the resulting string.
    """
    while len(string) < count:
        string = string + " "
    
    if len(string) > count:
        string = string[0: count]
    
    return string
