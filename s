#!/usr/bin/env python

import subprocess as sp
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("alias", nargs="?",
                    help="the replacement for the command")
parser.add_argument("arguments", nargs="*", default=[],
                    help="arguments that will be added to the argument")

parser.add_argument("-l", "--list", dest="list", action="store_true",
                    help="list mappings")
ag = parser.parse_args()

CFG = {
    "offset": 10,
    "mapping": {
        "document": {"cmd":   "sioyek",   "pre_args": []},
        "pdf":      {"alias": "document", "pre_args": []},

        "image":    {"cmd":   "nomacs",   "pre_args": []},

        "audio":    {"cmd":   "amberol",  "pre_args": []},
        "music":    {"alias": "audio",    "pre_args": []},

        "video":    {"cmd":   "mpv",      "pre_args": []}
    }
}

def run(command, pre_args):
    cmd_list = [command]
    cmd_list.extend(pre_args)
    cmd_list.extend(ag.arguments)
    return sp.run(cmd_list)

def offset(element, offset=CFG["offset"]):
    """
    calculates the amount of spaces until `offset` is reached for `element` length
    """
    element_length = len(element.strip(""))
    if element_length >= offset:
        return ""
    else:
        return " " * (offset - element_length)



if ag.list:
    for key, value in CFG["mapping"].items():
        value_str = ""
        for e_key, e_value in value.items():
            value_str += e_key + ": " + str(e_value) + ", "
        print(key, end="")
        print(offset(key), value_str.rstrip(", "))
else:
    for key, value in CFG["mapping"].items():
        if ag.alias in key: # matching
            if "alias" in value.keys():
                cmd = CFG["mapping"][value["alias"]]["cmd"]
            else:
                cmd = value["cmd"]

            run(cmd, value["pre_args"])
