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

    for label in object_labels:
        key, value = label.split(":")[0], label.split(":")[1]
        for separator in ["=", ":"]:
            if match_labels.split(separator)[0] == key and match_labels.split(separator)[1] == value:
                return True
            
    return False
