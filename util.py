"""Miscellaneous utility functions to aid the experiment"""

RESERVED_GUARD_NAMES = []
def get_guard_name():
    i = 0
    while True:
        i += 1

        guard_name = "node%d" % i
        if guard_name in RESERVED_GUARD_NAMES:
            continue # already used: skip it

        RESERVED_GUARD_NAMES.append(guard_name)
        return guard_name

def reset_guard_name_list():
    global RESERVED_GUARD_NAMES
    RESERVED_GUARD_NAMES = []
