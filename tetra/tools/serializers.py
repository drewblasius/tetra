import json


def is_serializable(x):
    try:
        json.dumps(x)
        return True
    except:
        return False
