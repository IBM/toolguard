import os
import subprocess
import sys
from typing import List
import venv

def run(venv_dir:str, packages:List[str]):
    # Create the virtual environment
    venv.create(venv_dir, with_pip=True)

    #install packages
    pip_executable = os.path.join(venv_dir, "bin", "pip")
    subprocess.run([pip_executable, "install"] + packages, check=True)