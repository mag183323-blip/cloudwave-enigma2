import json
import os

from .adapters import Track


SUPPORTED_AUDIO = (".mp3", ".ogg", ".oga", ".flac", ".m4a", ".aac", ".wav")


class LocalLibraryAdapter(object):
    """Indexes music already owned by the user on HDD/USB."""

    name = "Local Library"

    def __init__(self, root="/media/hdd/music"):
        self.root = root

    def search(self, query=""):
        if not os.path.isdir(self.root):
            return []
        needle = (query or "").lower().strip()
        tracks = []
        for folder, unused_dirs, files in os.walk(self.root):
            for filename in files:
                if not filename.lower().endswith(SUPPORTED_AUDIO):
                    continue
                full_path = os.path.join(folder, filename)
                title = os.path.splitext(filename)[0]
                artist = os.path.basename(folder)
                text = "%s %s" % (title, artist)
                if needle and needle not in text.lower():
                    continue
                tracks.append(Track(title, artist, full_path, self.name))
        return sorted(tracks, key=lambda item: item.label.lower())


class ArtistCatalog(object):
    """Small persistent catalog built from search results and local tracks."""

    def __init__(self, path="/etc/enigma2/cloudwave_artists.json"):
        self.path = path

    def load(self):
        try:
            with open(self.path, "r") as handle:
                value = json.load(handle)
                return value if isinstance(value, list) else []
        except (IOError, ValueError, TypeError):
            return []

    def update(self, tracks):
        names = set(self.load())
        for track in tracks:
            if track.artist:
                names.add(track.artist.strip())
        try:
            parent = os.path.dirname(self.path)
            if parent and not os.path.isdir(parent):
                os.makedirs(parent)
            with open(self.path, "w") as handle:
                json.dump(sorted(names, key=lambda item: item.lower()), handle)
        except (IOError, OSError):
            # A read-only image should not stop searching or playback.
            pass