#!/bin/sh
# CloudWave Enigma2 installer/updater.
# Usage:
#   wget -qO- https://raw.githubusercontent.com/USER/REPO/main/cloudwave_install.sh | sh
set -e

MANIFEST_URL="https://raw.githubusercontent.com/USER/REPO/main/manifest.json"
DEST="/usr/lib/enigma2/python/Plugins/Extensions/CloudWave"
TMP="/tmp/cloudwave-install"

rm -rf "$TMP"
mkdir -p "$TMP"

echo "CloudWave: checking latest release..."

python3 - "$MANIFEST_URL" "$DEST" "$TMP" <<'PY'
from __future__ import print_function
import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile

manifest_url, destination, work = sys.argv[1:4]

def get(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "CloudWave-Telnet-Installer"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()

data = json.loads(get(manifest_url).decode("utf-8", "replace"))
version = data.get("version", "")
url = data.get("url", "")
expected = (data.get("sha256", "") or "").lower()
if not version or not url:
    raise SystemExit("Invalid manifest.json")

archive = os.path.join(work, "cloudwave.zip")
with open(archive, "wb") as handle:
    handle.write(get(url))

digest = hashlib.sha256()
with open(archive, "rb") as handle:
    for block in iter(lambda: handle.read(131072), b""):
        digest.update(block)
actual = digest.hexdigest().lower()
if expected and actual != expected:
    raise SystemExit("SHA-256 verification failed")

extract = os.path.join(work, "extract")
os.makedirs(extract)
with zipfile.ZipFile(archive, "r") as package:
    root = os.path.abspath(extract) + os.sep
    for name in package.namelist():
        path = os.path.abspath(os.path.join(extract, name))
        if not path.startswith(root):
            raise SystemExit("Unsafe ZIP archive")
    package.extractall(extract)

source = os.path.join(extract, "CloudWave")
if not os.path.isdir(source):
    source = extract

parent = os.path.dirname(destination)
if not os.path.isdir(parent):
    os.makedirs(parent)
backup = destination + ".backup"
if os.path.isdir(destination):
    shutil.rmtree(backup, ignore_errors=True)
    shutil.copytree(destination, backup)
    shutil.rmtree(destination)
shutil.copytree(source, destination)
# Persist the manifest URL so the plugin can check updates on every launch.
settings = "/etc/enigma2/settings"
setting = "config.plugins.cloudwave.update_manifest=" + manifest_url
try:
    lines = []
    if os.path.exists(settings):
        with open(settings, "r") as handle:
            lines = handle.read().splitlines()
    replaced = False
    for index, line in enumerate(lines):
        if line.startswith("config.plugins.cloudwave.update_manifest="):
            lines[index] = setting
            replaced = True
    if not replaced:
        lines.append(setting)
    with open(settings, "w") as handle:
        handle.write("\n".join(lines) + "\n")
except (IOError, OSError) as error:
    print("Warning: could not save update URL:", error)
print("CloudWave %s installed successfully." % version)
PY

rm -rf "$TMP"
echo "Restart Enigma2 GUI to load CloudWave."
echo "Command: killall -HUP enigma2"