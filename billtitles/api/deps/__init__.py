from typing import List

from fastapi import Query

from .db import get_db

__all__ = [
    "get_db",
    "parse_list",
]


def remove_prefix(text: str, prefix: str):
    return text[text.startswith(prefix) and len(prefix) :]


def remove_postfix(text: str, postfix: str):
    if text.endswith(postfix):
        text = text[: -len(postfix)]
    return text


def parse_list(bills: List[str] = Query(None)):
    """Parse request query with bill numbers

    accepts strings formatted as lists with square brackets
    billnumbers can be in the format:
        ["117hr21","116hr2500"]
        ['117hr21','116hr2500']
        [117hr21,116hr2500]
        [117hr21, 116hr2500]
        [117hr21]
        or 117hr21
    """

    if bills is None:
        return

    # we already have a list, we can return
    if len(bills) > 1:
        return bills

    # if we don't start with a "[" and end with "]" it's just a normal entry
    flat_names = bills[0]
    if not flat_names.startswith("[") and not flat_names.endswith("]"):
        return bills

    flat_names = remove_prefix(flat_names, "[")
    flat_names = remove_postfix(flat_names, "]")

    names_list = flat_names.split(",")

    # remove `"`
    names_list = [remove_prefix(n.strip(), '"') for n in names_list]
    names_list = [remove_postfix(n.strip(), '"') for n in names_list]

    # remove `'`
    names_list = [remove_prefix(n.strip(), "'") for n in names_list]
    names_list = [remove_postfix(n.strip(), "'") for n in names_list]

    return names_list
