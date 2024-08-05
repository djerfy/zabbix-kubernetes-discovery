import re
import json

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

def ifLabelMatch(match_label=None, object_labels=None):
    """
    description: check if the object match a label
    return: bool
    """
    if match_label is None or match_label == "" or match_label == "*":
        return False
    
    if object_labels is None or object_labels == "" or object_labels == "*":
        return False
    
    object_labels = str(object_labels).replace("{", "").replace("}", "").replace("'", "").replace(" ", "").split(",")

    for label in object_labels:
        k, v = label.split(":")[0].replace('"', ''), label.split(":")[1].replace('"', '')

        for separator in ["=", ":"]:
            if len(match_label.split(separator)) != 2:
                continue
            if match_label.split(separator)[0] == k and match_label.split(separator)[1] == v:
                return True

    return False
