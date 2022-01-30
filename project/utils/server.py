import time


def get_time_now_in_ms() -> int:
    return int(time.time() * 1000.0)
