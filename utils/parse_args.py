from typing import Iterable


def parse_args(arguments: list, expected_cmd_args: Iterable) -> dict:
    res = {}
    for arg in arguments[1:]:
        separated_arg = arg.split('=')
        if len(separated_arg) != 2:
            continue
        key, val = separated_arg
        if key in expected_cmd_args:
            res[key] = val
    return res
