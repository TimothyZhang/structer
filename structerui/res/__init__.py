import os

def get_real_path(path):
    res_root = os.path.split(__file__)[0]
    return os.path.join(res_root, path)