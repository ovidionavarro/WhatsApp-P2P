import hashlib
from codes import m


def getShaRepr(data: str):
    return int(hashlib.sha1(data.encode()).hexdigest(), 16)%2**m
