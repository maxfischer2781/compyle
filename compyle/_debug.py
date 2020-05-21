import os
import sys

DEBUG_CHANNELS = {
    channel
    for channel in ("interpret", "frontend", "objects")
    if os.environ.get(f"DEBUG_{channel.upper()}")
}


def debug_print(channel: str, *args, **kwargs):
    if channel in DEBUG_CHANNELS:
        print(channel.upper() + ":", *args, file=sys.stderr, **kwargs)


def debug_enabled(channel: str):
    return channel in DEBUG_CHANNELS
