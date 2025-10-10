#!/usr/bin/env python3

import os
import re
import subprocess
import sys

# Path to Steam's main libraryfolders.vdf
vdf_path = os.path.expanduser("~/.steam/steam/steamapps/libraryfolders.vdf")

# Read & parse all library paths
with open(vdf_path, 'r') as f:
    content = f.read()
library_paths = [
    os.path.join(path, 'steamapps')
    for path in re.findall(r'"\d+"\s*{\s*"path"\s*"([^"]+)"', content)
]

# Precompile regexes
appid_pattern      = re.compile(r'"appid"\s+"(\d+)"')
name_pattern       = re.compile(r'"name"\s+"([^"]+)"')
stateflags_pattern = re.compile(r'"StateFlags"\s+"(\d+)"')
installdir_pattern = re.compile(r'"installdir"\s+"([^"]+)"')
type_pattern       = re.compile(r'"type"\s+"([^"]+)"')

# Build dict of {name: appid} for entries that are:
#   - StateFlags == "4"
#   - installdir exists under <steamapps>/common/<installdir>
#   - type != "Tool"
games = {}
for steamapps in library_paths:
    for manifest_fn in os.listdir(steamapps):
        if not (manifest_fn.startswith('appmanifest') and manifest_fn.endswith('.acf')):
            continue

        path = os.path.join(steamapps, manifest_fn)
        with open(path, 'r') as mf:
            data = mf.read()

        appid_match      = appid_pattern.search(data)
        name_match       = name_pattern.search(data)
        stateflags_match = stateflags_pattern.search(data)
        installdir_match = installdir_pattern.search(data)
        type_match       = type_pattern.search(data)

        # Skip if any required field is missing
        if not (appid_match and name_match and stateflags_match and installdir_match and type_match):
            continue

        # 1) Only fully‐installed (StateFlags == "4")
        if stateflags_match.group(1) != "4":
            continue

        # 2) Exclude anything of type "Tool" (i.e. runtimes, SDKs, etc.)
        if type_match.group(1).lower() == "tool":
            continue

        # 3) Ensure <steamapps>/common/<installdir> is a real directory
        installdir = installdir_match.group(1)
        common_dir = os.path.join(steamapps, 'common', installdir)
        if not os.path.isdir(common_dir):
            continue

        # Passed all checks → add it
        games[name_match.group(1)] = appid_match.group(1)

if not games:
    print("No startable games found.")
    sys.exit(1)

# Pipe names into fzf, capture only the chosen line
fzf_proc = subprocess.Popen(
    ['fzf'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)
stdout, _ = fzf_proc.communicate('\n'.join(games.keys()))
selection = stdout.strip()

# If a game was selected, launch it via Steam in the background, silently
if selection:
    subprocess.Popen(
        ['steam', '-silent', f'steam://run/{games[selection]}'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
