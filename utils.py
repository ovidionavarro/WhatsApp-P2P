import hashlib
import shutil
import os
from codes import m


def getShaRepr(data: str):
    return int(hashlib.sha1(data.encode()).hexdigest(), 16)%2**m


def rem_dir(dir: str):
    # Normaliza la ruta para el sistema operativo actual
    dir = os.path.normpath(dir)
    
    if os.path.exists(dir):
        shutil.rmtree(dir)

def create_folder(dir: str):
    if not os.path.exists(dir):
        os.makedirs(dir)