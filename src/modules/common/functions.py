import re

def ifObjectMatch(object_list=None, object_name=None):
    """
    description: check if the object is in list
    return: bool
    """
    if object_list is None or object_list == "" or object_list == "*":
        return False

    if object_name is None or object_name == "" or object_name == "*":
        return False

    if type(object_list) == str:
        object_list = object_list.split(",")

    if type(object_list) != list:
        return False

    reg_list = map(re.compile, object_list)

    if any(reg.match(object_name) for reg in reg_list):
        return True

    return False

