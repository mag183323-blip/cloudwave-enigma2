try:
    from Components.config import (
        config, ConfigSubsection, ConfigText, ConfigYesNo, getConfigListEntry
    )

    config.plugins.cloudwave = ConfigSubsection()
    config.plugins.cloudwave.soundcloud_url = ConfigText(
        default="", fixed_size=False
    )
    config.plugins.cloudwave.youtube_url = ConfigText(
        default="", fixed_size=False
    )
    config.plugins.cloudwave.search_archive = ConfigYesNo(default=True)
    config.plugins.cloudwave.update_manifest = ConfigText(
        default="", fixed_size=False
    )

    def entries():
        return [
            getConfigListEntry(
                "SoundCloud API/Proxy URL", config.plugins.cloudwave.soundcloud_url
            ),
            getConfigListEntry(
                "YouTube API/Proxy URL", config.plugins.cloudwave.youtube_url
            ),
            getConfigListEntry(
                "Search Internet Archive", config.plugins.cloudwave.search_archive
            ),
            getConfigListEntry(
                "Update manifest URL", config.plugins.cloudwave.update_manifest
            ),
        ]
except ImportError:
    # Allows static inspection and packaging outside an Enigma2 runtime.
    def entries():
        return []