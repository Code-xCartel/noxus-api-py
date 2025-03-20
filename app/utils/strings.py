import time
import random

char_strings = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def generate_unique_id(length=8):
    timestamp = int(time.time() * 1000)  # Milliseconds since epoch
    random_string = "".join(random.choices(char_strings, k=length))
    unique_id = f"{timestamp}{random_string}"
    return f"NOX-{unique_id[:length]}"


class JSONResponse:
    def __init__(self, details):
        self.details = details

    def __repr__(self):
        return self.details
