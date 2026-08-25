from Plugins.Plugin import PluginDescriptor
from .ui import CloudWaveScreen


def main(session, **kwargs):
    session.open(CloudWaveScreen)


def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name="CloudWave",
            description="Multi-source audio search and player",
            where=PluginDescriptor.WHERE_EXTENSIONSMENU,
            fnc=main,
        ),
        PluginDescriptor(
            name="CloudWave",
            description="Multi-source audio search and player",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            fnc=main,
        ),
    ]