#!/usr/bin/env python3

import os
import re
import subprocess

# Path to Steam's libraryfolders.vdf
vdf_path = os.path.expanduser("~/.steam/steam/steamapps/libraryfolders.vdf")

# Read and parse library paths using regex
with open(vdf_path, 'r') as f:
    content = f.read()
library_paths = [os.path.join(path, 'steamapps') for path in re.findall(r'"\d+"\s*{\s*"path"\s*"([^"]+)"', content)]

# Compile regex patterns for efficiency
appid_pattern = re.compile(r'"appid"\s+"(\d+)"')
name_pattern = re.compile(r'"name"\s+"([^"]+)"')
stateflags_pattern = re.compile(r'"StateFlags"\s+"(\d+)"')

# Extract game names and their corresponding AppIDs
games = {}
for steamapps in library_paths:
    manifests = [f for f in os.listdir(steamapps) if f.startswith('appmanifest') and f.endswith('.acf')]
    for manifest in manifests:
        with open(os.path.join(steamapps, manifest), 'r') as f:
            data = f.read()
        appid_match = appid_pattern.search(data)
        name_match = name_pattern.search(data)
        stateflags_match = stateflags_pattern.search(data)
        if appid_match and name_match and stateflags_match:
            if stateflags_match.group(1) == "4":
                games[name_match.group(1)] = appid_match.group(1)

# Use fzf to select a game
fzf = subprocess.Popen(
    ['fzf'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)
stdout, _ = fzf.communicate('\n'.join(games.keys()))
selection = stdout.strip()

# Launch the selected game via Steam silently in the background
if selection:
    subprocess.Popen(
        ['steam', '-silent', f'steam://run/{games[selection]}'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

