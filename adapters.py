import json
import urllib.parse
import urllib.request


class Track(object):
    def __init__(self, title, artist="", stream_url="", source=""):
        self.title = title or "Untitled"
        self.artist = artist or source
        self.stream_url = stream_url or ""
        self.source = source

    @property
    def label(self):
        prefix = "[%s] " % self.source if self.source else ""
        return "%s%s - %s" % (prefix, self.title, self.artist)


def _get_json(url, timeout=12):
    request = urllib.request.Request(
        url, headers={"User-Agent": "CloudWave/0.1 Enigma2"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8", "replace"))


class InternetArchiveAdapter(object):
    name = "Internet Archive"

    def search(self, query):
        fields = "identifier,title,creator,format"
        params = urllib.parse.urlencode({
            "q": 'mediatype:audio AND ("%s")' % query,
            "fl[]": fields.split(","),
            "rows": 20,
            "output": "json",
        }, doseq=True)
        data = _get_json(
            "https://archive.org/advancedsearch.php?%s" % params
        )
        tracks = []
        for item in data.get("response", {}).get("docs", []):
            identifier = item.get("identifier")
            if not identifier:
                continue
            # Metadata endpoint normally exposes downloadable files; this
            # reference is resolved lazily by the player/browser in a later
            # iteration.
            tracks.append(Track(
                item.get("title", identifier),
                item.get("creator", ""),
                "https://archive.org/metadata/%s" % identifier,
                self.name,
            ))
        return tracks


class ProxyAdapter(object):
    def __init__(self, name, endpoint):
        self.name = name
        self.endpoint = endpoint.strip()

    def search(self, query):
        if not self.endpoint:
            return []
        separator = "&" if "?" in self.endpoint else "?"
        data = _get_json(
            self.endpoint + separator + urllib.parse.urlencode({"q": query})
        )
        results = data.get("results", data if isinstance(data, list) else [])
        tracks = []
        for item in results[:30]:
            if not isinstance(item, dict):
                continue
            tracks.append(Track(
                item.get("title"),
                item.get("artist") or item.get("author"),
                item.get("stream_url") or item.get("url"),
                self.name,
            ))
        return tracks


def search_all(query, archive=True, soundcloud_url="", youtube_url="",
               local_path="/media/hdd/music"):
    from .library import LocalLibraryAdapter, ArtistCatalog

    adapters = []
    adapters.append(LocalLibraryAdapter(local_path))
    if archive:
        adapters.append(InternetArchiveAdapter())
    adapters.extend([
        ProxyAdapter("SoundCloud", soundcloud_url),
        ProxyAdapter("YouTube", youtube_url),
    ])
    result = []
    errors = []
    for adapter in adapters:
        try:
            result.extend(adapter.search(query))
        except Exception as error:
            if getattr(adapter, "endpoint", None):
                errors.append("%s: %s" % (adapter.name, error))
    ArtistCatalog().update(result)
    return result, errors