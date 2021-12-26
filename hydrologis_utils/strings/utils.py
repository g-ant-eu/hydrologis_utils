def check_same_name( strings, checkString ):
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
    