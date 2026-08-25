# CloudWave Enigma2 Plugin

إضافة MVP للبحث وتشغيل المحتوى الصوتي من أكثر من مصدر داخل Enigma2.

## ما يعمل في النسخة الأولية

- واجهة بسيطة قابلة للتحكم بالريموت.
- بحث موحد في:
  - Internet Archive (يعمل مباشرة).
  - SoundCloud عبر Proxy/API قابل للضبط.
  - YouTube عبر Proxy/API قابل للضبط.
- تشغيل روابط الصوت باستخدام مشغل Enigma2.
- فهرسة مكتبة الأغاني المحلية من `/media/hdd/music`.
- حفظ أسماء الفنانين التي تظهر في نتائج البحث داخل `/etc/enigma2/cloudwave_artists.json`.
- فحص تلقائي لوجود إصدار أحدث عند فتح البلوجن.
- تحديث اختياري بعد موافقة المستخدم مع التحقق من SHA-256.
- تصميم Adapter مستقل لإضافة مصادر أخرى لاحقًا.
- بدون مكتبات Python خارجية.

## التثبيت

انسخ مجلد `CloudWave` إلى:

```text
/usr/lib/enigma2/python/Plugins/Extensions/CloudWave/
```

ثم أعد تشغيل واجهة Enigma2:

```text
Menu > Setup > System > Restart GUI
```

## إعداد المصادر

من داخل البلوجن اضغط `Menu` وافتح الإعدادات. يمكن ضبط:

- `SoundCloud API URL`: نقطة بحث تعيد JSON بالشكل:
  `{"results":[{"title":"...","artist":"...","stream_url":"http://..."}]}`
- `YouTube API URL`: نفس الشكل.

مهم: لا يبحث البلوجن في “كل الإنترنت” تلقائيًا. كل موقع يحتاج Adapter أو API خاصًا به؛ النظام مصمم لإضافة المواقع تدريجيًا بدون تغيير الواجهة.

يمكن وضع الأغاني التي يملكها المستخدم على الهارد أو USB داخل:

```text
/media/hdd/music/
```

ويُفضّل تنظيمها في مجلدات باسم الفنان. البلوجن يفهرس صيغ MP3 وOGG وFLAC
وM4A وAAC وWAV، ولا يقوم بتنزيل أو نسخ محتوى محمي من المواقع.

## التوافق

الكود يستخدم Python القياسي فقط ويحاول تجنب تفاصيل صورة واحدة. التوافق العملي يعتمد على نسخة Enigma2 ووجود:

- `Components`
- `Screens`
- `enigma.eServiceReference`

تم استهداف Python 3.8+، ويظل الكود متوافقًا مع 3.13 و3.14 من ناحية اللغة القياسية.

## التحديث من GitHub

ضع ملفًا باسم `manifest.json` في مستودع GitHub، مثل:

```json
{
  "version": "0.3.0",
  "url": "https://github.com/USERNAME/REPOSITORY/releases/download/v0.3.0/cloudwave-enigma2.zip",
  "sha256": "ضع هنا قيمة SHA-256 للملف",
  "notes": "تحسين البحث وإضافة تصنيفات الفنانين"
}
```

ثم ضع رابط الملف الخام في إعداد `Update manifest URL`، مثل:

```text
https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/manifest.json
```

يجب أن يكون رابط التحديث HTTPS وأن يحتوي الـZIP على مجلد `CloudWave`.