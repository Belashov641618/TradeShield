import os
import subprocess

def gitpull(directory:str):
    if os.path.isfile(directory): directory = os.path.dirname(directory)
    directory = os.path.abspath(directory)
    result = subprocess.run(
        ["git", "pull"],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    return result.stdout
