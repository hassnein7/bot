# تكوين البوت
import os

# توكن البوت الخاص بك من BotFather
# استخدام متغيرات البيئة للتوافق مع منصة Render و Replit
# في Replit، يمكنك تعيين المتغيرات من خلال لوحة التحكم (Secrets)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7549109713:AAEfZQmJSILw8y2ip3YnkqZgeOF4lT3D4IU")

# طباعة رسالة تشخيصية للمساعدة في تحديد المشكلات
print(f"تم تحميل ملف التكوين. حالة BOT_TOKEN: {'تم تعيينه' if BOT_TOKEN else 'غير معين!'}")


# إعدادات أخرى
DATABASE_FILE = "accounting_data.json"
