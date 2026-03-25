import json
from jsondiff import diff

def list_to_dict(lst):  
    return {str(i): value for i, value in enumerate(lst)}

def calculate_similarity(target_json, actual_json):
    if(target_json is None or actual_json is None):
        return 1
    if isinstance(target_json, list):  
        target_json = list_to_dict(target_json) 
    if isinstance(actual_json, list):
        actual_json = list_to_dict(actual_json)
    keys1 = set(target_json.keys())
    keys2 = set(actual_json.keys())
    if len(keys1) == 0 and len(keys2) == 0:  
        return 1  
    elif len(keys1) == 0 or len(keys2) == 0:  
        return 0
    common_keys = keys1.intersection(keys2)
    key_similarity = len(common_keys) / max(len(keys1), len(keys2))
    value_similarity = 0.0
    for key in common_keys:
        value1 = target_json[key]
        value2 = actual_json[key]
        if value1 == value2:
            value_similarity += 1.0
    if len(common_keys) > 0:
        value_similarity /= len(common_keys)
    overall_similarity = (key_similarity + value_similarity) / 2.0
    scaled_similarity = overall_similarity * 100000
    return scaled_similarity