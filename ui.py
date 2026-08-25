import threading

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Screens.Screen import Screen
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from enigma import eServiceReference

from .adapters import search_all
from .config import config
from .updater import check_for_update, install_update
from .version import VERSION


class CloudWaveScreen(Screen):
    skin = """
        <screen name="CloudWaveScreen" position="center,center" size="1200,680"
                title="CloudWave" flags="wfNoBorder"
                backgroundColor="#10141c">
            <widget name="brand" position="45,28" size="1110,54"
                    font="Regular;34" foregroundColor="#ffffff" />
            <widget name="header" position="48,86" size="1100,42"
                    font="Regular;23" foregroundColor="#9aa7bb" />
            <widget name="list" position="45,145" size="1110,430"
                    scrollbarMode="showOnDemand"
                    backgroundColor="#1b2230" foregroundColor="#ffffff"
                    foregroundColorSelected="#ffffff"
                    backgroundColorSelected="#2f78d0"
                    font="Regular;25" />
            <widget name="footer" position="48,605" size="1100,40"
                    font="Regular;21" foregroundColor="#9aa7bb" />
        </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.tracks = []
        self["brand"] = Label("♫  CLOUDWAVE")
        self["header"] = Label("بحث موسيقى من أكثر من مصدر")
        self["list"] = MenuList([])
        self["footer"] = Label("OK بحث / تشغيل   |   MENU بحث جديد   |   EXIT خروج")
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "MenuActions"],
            {
                "ok": self.ok_action,
                "cancel": self.close,
                "menu": self.show_search,
                "red": self.show_search,
            },
            -1,
        )
        self.onLayoutFinish.append(self.check_update)

    def check_update(self):
        manifest = config.plugins.cloudwave.update_manifest.value
        if not manifest:
            return
        def worker():
            try:
                info = check_for_update(manifest)
            except Exception:
                info = None
            self._pending_update = info
            self.update_timer = __import__("enigma").eTimer()
            self.update_timer.callback.append(self._update_result)
            self.update_timer.start(10, True)
        threading.Thread(target=worker).start()

    def _update_result(self):
        info = getattr(self, "_pending_update", None)
        if not info:
            return
        text = "توجد نسخة أحدث %s\n\n%s\n\nهل تريد التحديث الآن؟" % (
            info.version, info.notes
        )
        self.session.openWithCallback(
            lambda answer: self.start_update(info) if answer else None,
            MessageBox, text=text, type=MessageBox.TYPE_YESNO
        )

    def start_update(self, info):
        self["footer"].setText("جاري تنزيل التحديث %s..." % info.version)
        def worker():
            try:
                install_update(info)
                message = "تم التحديث إلى %s. أعد تشغيل واجهة Enigma2." % info.version
            except Exception as error:
                message = "فشل التحديث: %s" % error
            self._update_message = message
            self.update_timer = __import__("enigma").eTimer()
            self.update_timer.callback.append(self._show_update_message)
            self.update_timer.start(10, True)
        threading.Thread(target=worker).start()

    def _show_update_message(self):
        self.session.open(MessageBox, text=self._update_message,
                          type=MessageBox.TYPE_INFO, timeout=8)

    def show_search(self):
        self.session.openWithCallback(
            self.search_callback, InputBox, title="اكتب اسم الفنان أو التراك:"
        )

    def ok_action(self):
        if self.tracks:
            self.play_selected()
        else:
            self.show_search()

    def search_callback(self, query):
        if not query:
            return
        self["header"].setText("CloudWave - جاري البحث عن: %s" % query)
        self["footer"].setText("انتظر...")

        def worker():
            tracks, errors = search_all(
                query,
                config.plugins.cloudwave.search_archive.value,
                config.plugins.cloudwave.soundcloud_url.value,
                config.plugins.cloudwave.youtube_url.value,
            )
            self._search_done(tracks, errors)

        threading.Thread(target=worker).start()

    def _search_done(self, tracks, errors):
        self.tracks = tracks
        self["list"].setList([track.label for track in tracks])
        self["footer"].setText(
            "%d نتيجة | OK تشغيل | MENU بحث جديد%s" %
            (len(tracks), (" | " + " ; ".join(errors)) if errors else "")
        )

    def play_selected(self):
        index = self["list"].getSelectedIndex()
        if index < 0 or index >= len(self.tracks):
            return
        track = self.tracks[index]
        if not track.stream_url:
            self["footer"].setText("هذه النتيجة لا تحتوي على رابط تشغيل مباشر")
            return
        self.session.nav.playService(
            eServiceReference(4097, 0, track.stream_url)
        )
