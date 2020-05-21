from typing import Set

import sys
import enum


class DEBUG_CHANNEL(enum.Enum):
    INTERPRET = enum.auto()
    PARSING = enum.auto()
    TRANSPYLE = enum.auto()


ENABLED_CHANNELS: Set[DEBUG_CHANNEL] = set()


def debug_print(channel: DEBUG_CHANNEL, *args, **kwargs):
    if channel in ENABLED_CHANNELS:
        print(channel.name.ljust(10) + ":", *args, file=sys.stderr, **kwargs)


def debug_enabled(channel: DEBUG_CHANNEL):
    return channel in ENABLED_CHANNELS
