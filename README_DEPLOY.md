# دليل نشر بوت المحاسبة الشخصية على المنصات السحابية

هذا الدليل يشرح كيفية نشر بوت المحاسبة الشخصية على منصات سحابية مختلفة ليعمل على مدار الساعة (24/7).

## النشر على Heroku

### المتطلبات

1. حساب على [Heroku](https://www.heroku.com/)
2. تثبيت [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. حساب على [GitHub](https://github.com/) (اختياري)

### خطوات النشر

1. قم بتسجيل الدخول إلى Heroku CLI:

```
heroku login
```

2. قم بإنشاء تطبيق جديد على Heroku:

```
heroku create اسم-التطبيق-الخاص-بك
```

3. قم بتعيين متغيرات البيئة المطلوبة:

```
heroku config:set BOT_TOKEN=توكن_البوت_الخاص_بك
heroku config:set APP_URL=https://اسم-التطبيق-الخاص-بك.herokuapp.com
```

4. قم برفع الكود إلى Heroku:

```
git init
git add .
git commit -m "Initial commit"
git push heroku master
```

5. تأكد من تشغيل مثيل واحد على الأقل من التطبيق:

```
heroku ps:scale web=1
```

## النشر على Railway

### المتطلبات

1. حساب على [Railway](https://railway.app/)
2. مستودع GitHub (اختياري)

### خطوات النشر

1. قم بتسجيل الدخول إلى Railway باستخدام حساب GitHub أو Google.
2. انقر على "New Project" ثم اختر "Deploy from GitHub" أو "Empty Project".
3. إذا اخترت "Empty Project"، قم بإضافة خدمة جديدة واختر "GitHub Repo" أو "Empty Service".
4. قم بتعيين متغيرات البيئة التالية في قسم "Variables":
   - `BOT_TOKEN`: توكن البوت الخاص بك
   - `APP_URL`: سيتم توفيره تلقائياً بواسطة Railway (استخدم عنوان URL المقدم في قسم "Settings")
5. انتظر حتى يتم نشر التطبيق.

## النشر على PythonAnywhere

### المتطلبات

1. حساب على [PythonAnywhere](https://www.pythonanywhere.com/)

### خطوات النشر

1. قم بتسجيل الدخول إلى PythonAnywhere.
2. انتقل إلى قسم "Consoles" وافتح وحدة تحكم Bash جديدة.
3. قم بنسخ المشروع الخاص بك باستخدام Git أو قم بتحميل الملفات يدوياً:

```
git clone https://github.com/yourusername/accounting-bot.git
cd accounting-bot
pip install -r requirements.txt
```

4. انتقل إلى قسم "Web" وانقر على "Add a new web app".
5. اختر "Manual configuration" ثم اختر إصدار Python المناسب.
6. قم بتعديل ملف WSGI ليشير إلى تطبيقك.
7. قم بإعداد متغيرات البيئة في ملف `.env` أو من خلال لوحة التحكم.
8. قم بإعداد مهمة مجدولة (Scheduled Task) لتشغيل البوت:
   - انتقل إلى قسم "Tasks".
   - أضف مهمة جديدة تقوم بتشغيل البوت كل دقيقة أو كل ساعة.

## ملاحظات هامة

1. تأكد من أن توكن البوت الخاص بك صحيح وتم تعيينه بشكل صحيح في متغيرات البيئة.
2. قد تحتاج إلى تعديل ملف `Procfile` اعتماداً على المنصة التي تستخدمها.
3. بعض المنصات السحابية المجانية قد تضع البوت في وضع السكون بعد فترة من عدم النشاط. يمكنك استخدام خدمات مثل [UptimeRobot](https://uptimerobot.com/) للحفاظ على نشاط البوت.

## استكشاف الأخطاء وإصلاحها

1. إذا لم يعمل البوت، تحقق من سجلات التطبيق (logs) للحصول على معلومات حول الأخطاء.
2. تأكد من أن جميع المتغيرات البيئية المطلوبة تم تعيينها بشكل صحيح.
3. تحقق من أن البوت يستخدم webhook بدلاً من polling في البيئة السحابية.

للمزيد من المساعدة، راجع وثائق المنصة السحابية التي تستخدمها أو وثائق مكتبة python-telegram-bot.