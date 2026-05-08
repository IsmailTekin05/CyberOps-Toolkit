import os

def ensure_dir(path):
    directory = os.path.dirname(path) if "." in os.path.basename(path) else path
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return path
