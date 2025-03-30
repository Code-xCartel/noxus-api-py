import hashlib
import random
import socket
import time


def generate_unique_id(*args):
    """
    Generates a universally unique ID.
    Any arguments only create more randomness.
    """
    t = int(time.time() * 1000)
    r = int(random.random() * 100000000000000000)
    try:
        a = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        # if we can't get a network address, just imagine one
        a = random.random() * 100000000000000000
    data = f"{t} {r} {a} {args}".encode()
    data = hashlib.md5(data).hexdigest()

    return f"NOX-{data}"


class JSONResponse:
    def __init__(self, details):
        self.details = details

    def __repr__(self):
        return self.details
