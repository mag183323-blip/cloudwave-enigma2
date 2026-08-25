import hashlib
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile

from .version import VERSION


class UpdateInfo(object):
    def __init__(self, version, url, sha256="", notes=""):
        self.version = version
        self.url = url
        self.sha256 = (sha256 or "").lower()
        self.notes = notes or ""


def _download(url, destination):
    request = urllib.request.Request(
        url, headers={"User-Agent": "CloudWave-Updater/%s" % VERSION}
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        with open(destination, "wb") as output:
            shutil.copyfileobj(response, output)


def _version_tuple(value):
    parts = []
    for item in (value or "0").split("."):
        digits = ""
        for char in item:
            if char.isdigit():
                digits += char
            else:
                break
        parts.append(int(digits or "0"))
    return tuple((parts + [0, 0, 0])[:3])


def check_for_update(manifest_url):
    if not manifest_url:
        return None
    request = urllib.request.Request(
        manifest_url, headers={"User-Agent": "CloudWave-Updater/%s" % VERSION}
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        data = json.loads(response.read().decode("utf-8", "replace"))
    remote = data.get("version", "")
    url = data.get("url", "")
    if not remote or not url or _version_tuple(remote) <= _version_tuple(VERSION):
        return None
    return UpdateInfo(remote, url, data.get("sha256", ""), data.get("notes", ""))


def install_update(info):
    """Download, verify, and replace this plugin atomically where possible."""
    temp_dir = tempfile.mkdtemp(prefix="cloudwave-update-")
    archive_path = os.path.join(temp_dir, "update.zip")
    extract_dir = os.path.join(temp_dir, "extract")
    target = os.path.dirname(os.path.abspath(__file__))
    try:
        _download(info.url, archive_path)
        digest = hashlib.sha256()
        with open(archive_path, "rb") as handle:
            for block in iter(lambda: handle.read(1024 * 128), b""):
                digest.update(block)
        if info.sha256 and digest.hexdigest().lower() != info.sha256:
            raise RuntimeError("SHA-256 verification failed")

        os.makedirs(extract_dir)
        with zipfile.ZipFile(archive_path, "r") as archive:
            names = archive.namelist()
            # Prevent ZIP path traversal.
            for name in names:
                destination = os.path.abspath(os.path.join(extract_dir, name))
                if not destination.startswith(os.path.abspath(extract_dir) + os.sep):
                    raise RuntimeError("Unsafe update archive")
            archive.extractall(extract_dir)

        source = os.path.join(extract_dir, "CloudWave")
        if not os.path.isdir(source):
            source = extract_dir
        for name in os.listdir(source):
            source_file = os.path.join(source, name)
            target_file = os.path.join(target, name)
            if os.path.isdir(source_file):
                if os.path.exists(target_file):
                    shutil.rmtree(target_file)
                shutil.copytree(source_file, target_file)
            else:
                shutil.copy2(source_file, target_file)
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)