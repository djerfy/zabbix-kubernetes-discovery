import re
import json

def matchLabels(match_labels=None, object_labels=None):
    """
    description: check if the object match labels
    return: bool
    """
    for i in [match_labels, object_labels]:
        if i is None or i == [] or i == "" or i == "*":
            return False

    object_labels = str(object_labels).replace("{", "").replace("}", "").replace("'", "").replace(" ", "").split(",")

    for object_label in object_labels:
        key, value = object_label.split(":")[0], object_label.split(":")[1]
        for match_label in match_labels:
            for separator in ["=", ":"]:
                if match_label.split(separator)[0] == key and match_label.split(separator)[1] == value:
                    return True

    return False
