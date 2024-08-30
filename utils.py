import hashlib
from codes import M


def getShaRepr(data: str):
    return int(hashlib.sha1(data.encode()).hexdigest(), 16)%2**M
