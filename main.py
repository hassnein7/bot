import logging
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from config import BOT_TOKEN
import utils
from accounting_knowledge import get_accounting_info, get_accounting_topics
from financial_analysis import analyze_report, check_financial_statements

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # تغيير مستوى التسجيل من INFO إلى DEBUG للحصول على معلومات أكثر تفصيلاً
)

logger = logging.getLogger(__name__)
# حالات المحادثة
STATE_NORMAL = 0
STATE_ANALYZING_REPORT = 1
STATE_ANALYZING_STATEMENTS = 2

# وظيفة البداية
# وظيفة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرد على أمر /start"""
    user = update.effective_user
    # تهيئة بيانات المستخدم إذا لم تكن موجودة
    if not context.user_data:
        context.user_data['state'] = STATE_NORMAL
        context.user_data['temp_data'] = {}
    
    await update.message.reply_text(
        f"مرحباً {user.first_name}! 👋\n\n"
        "أنا مساعدك المحاسبي الذكي. أمتلك خبرة تعادل محاسب محترف عمل لمدة 60 سنة في مجال المحاسبة.\n\n"
        "يمكنني مساعدتك في فهم المفاهيم المحاسبية وشرحها بطريقة مبسطة وتعليمية، كما يمكنني فحص وتحليل التقارير المالية وتقديم النصائح المحاسبية المتخصصة.\n\n"
        "استخدم الأوامر التالية:\n"
        "/topics - عرض قائمة المواضيع المحاسبية المتاحة\n"
        "/info [اسم الموضوع] - الحصول على معلومات حول موضوع محاسبي معين\n"
        "/analyze_report - تحليل تقرير مالي وتقديم ملاحظات وتوصيات\n"
        "/analyze_statements - تحليل القوائم المالية (الميزانية، قائمة الدخل، التدفقات النقدية)\n"
        "/help - عرض قائمة المساعدة\n\n"
        "يمكنك ببساطة أن تسألني أي سؤال محاسبي وسأحاول الإجابة عليه، أو يمكنك إرسال تقارير مالية لي لفحصها وتحليلها!"
    )

# وظيفة تحليل التقرير المالي
async def analyze_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية تحليل تقرير مالي"""
    context.user_data['state'] = STATE_ANALYZING_REPORT
    await update.message.reply_text(
        "📊 تحليل التقرير المالي\n\n"
        "يرجى إرسال التقرير المالي الذي ترغب في تحليله. يمكنك إرسال النص مباشرة أو كملف نصي.\n\n"
        "سأقوم بتحليل التقرير وتقديم ملاحظات وتوصيات بناءً على خبرتي المحاسبية."
    )

# وظيفة تحليل القوائم المالية
async def analyze_statements_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية تحليل القوائم المالية"""
    context.user_data['state'] = STATE_ANALYZING_STATEMENTS
    await update.message.reply_text(
        "📑 تحليل القوائم المالية\n\n"
        "يرجى إرسال القوائم المالية التي ترغب في تحليلها (الميزانية، قائمة الدخل، التدفقات النقدية).\n\n"
        "يمكنك إرسال كل قائمة بشكل منفصل أو جميعها معاً. سأقوم بتحليلها وتقديم تقرير مفصل."
    )

# وظيفة عرض المواضيع المحاسبية
async def topics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المواضيع المحاسبية المتاحة"""
    topics = get_accounting_topics()
    
    # تقسيم المواضيع إلى أزرار
    keyboard = []
    for topic in topics:
        keyboard.append([InlineKeyboardButton(topic, callback_data=f"topic_{topic}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📚 المواضيع المحاسبية المتاحة:\n\n"
        "اختر موضوعاً للحصول على معلومات مفصلة:",
        reply_markup=reply_markup
    )

# وظيفة الحصول على معلومات حول موضوع محاسبي
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الحصول على معلومات حول موضوع محاسبي معين"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ يرجى تحديد اسم الموضوع بعد الأمر.\n"
            "مثال: /info المحاسبة المالية\n\n"
            "استخدم /topics لعرض قائمة المواضيع المتاحة."
        )
        return
    
    topic = " ".join(context.args)
    info = get_accounting_info(topic)
    
    if info:
        await update.message.reply_text(f"📘 {topic}\n\n{info}")
    else:
        await update.message.reply_text(
            f"⚠️ لم يتم العثور على معلومات حول '{topic}'.\n"
            "استخدم /topics لعرض قائمة المواضيع المتاحة."
        )

# وظيفة المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المساعدة"""
    await update.message.reply_text(
        "🔍 قائمة المساعدة\n\n"
        "الأوامر المتاحة:\n"
        "/start - بدء محادثة جديدة مع البوت\n"
        "/topics - عرض قائمة المواضيع المحاسبية المتاحة\n"
        "/info [اسم الموضوع] - الحصول على معلومات حول موضوع محاسبي معين\n"
        "/analyze_report - تحليل تقرير مالي وتقديم ملاحظات وتوصيات\n"
        "/analyze_statements - تحليل القوائم المالية (الميزانية، قائمة الدخل، التدفقات النقدية)\n"
        "/help - عرض هذه القائمة\n\n"
        "يمكنك أيضاً أن تسألني مباشرة أي سؤال محاسبي وسأحاول الإجابة عليه بأفضل ما لدي من معرفة."
    )

# معالجة الرسائل النصية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل النصية الواردة"""
    if not context.user_data:
        context.user_data['state'] = STATE_NORMAL
        context.user_data['temp_data'] = {}
    
    state = context.user_data.get('state', STATE_NORMAL)
    text = update.message.text
    
    if state == STATE_ANALYZING_REPORT:
        # تحليل التقرير المالي
        analysis = analyze_report(text)
        await update.message.reply_text(f"📊 تحليل التقرير المالي:\n\n{analysis}")
        context.user_data['state'] = STATE_NORMAL
    
    elif state == STATE_ANALYZING_STATEMENTS:
        # تحليل القوائم المالية
        analysis = check_financial_statements(text)
        await update.message.reply_text(f"📑 تحليل القوائم المالية:\n\n{analysis}")
        context.user_data['state'] = STATE_NORMAL
    
    else:
        # معالجة الأسئلة المحاسبية العامة
        # هنا يمكن استخدام نموذج لغوي متقدم للإجابة على الأسئلة المحاسبية
        # لكن في هذا المثال سنستخدم إجابة بسيطة
        await update.message.reply_text(
            f"شكراً على سؤالك حول '{text}'.\n\n"
            "يمكنك استخدام /topics لاستعراض المواضيع المحاسبية المتاحة، "
            "أو /info [اسم الموضوع] للحصول على معلومات حول موضوع محدد."
        )

# معالجة ردود الأزرار
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة ردود الأزرار"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("topic_"):
        topic = data[6:]  # استخراج اسم الموضوع
        info = get_accounting_info(topic)
        
        if info:
            await query.message.reply_text(f"📘 {topic}\n\n{info}")
        else:
            await query.message.reply_text(
                f"⚠️ لم يتم العثور على معلومات حول '{topic}'.\n"
                "استخدم /topics لعرض قائمة المواضيع المتاحة."
            )

# الدالة الرئيسية
def main():
    """تشغيل البوت"""
    # طباعة معلومات تشخيصية
    logger.info(f"بدء تشغيل البوت...")
    logger.info(f"قيمة BOT_TOKEN: {'تم تعيينها' if BOT_TOKEN else 'غير معينة!'}")
    
    # التحقق من وجود توكن البوت
    if not BOT_TOKEN:
        logger.error("خطأ: لم يتم تعيين BOT_TOKEN. يرجى تعيين متغير البيئة BOT_TOKEN.")
        print("خطأ: لم يتم تعيين BOT_TOKEN. يرجى تعيين متغير البيئة BOT_TOKEN.")
        return
    
    # إنشاء تطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("topics", topics_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("analyze_report", analyze_report_command))
    application.add_handler(CommandHandler("analyze_statements", analyze_statements_command))
    
    # إضافة معالج الرسائل النصية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # إضافة معالج ردود الأزرار
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # تشغيل البوت
    # التحقق من بيئة التشغيل (Replit أو غيرها)
    is_replit = os.environ.get("REPL_ID") is not None
    port = int(os.environ.get("PORT", 8443))
    app_url = os.environ.get("APP_URL", "")
    
    if is_replit:
        # استخدام polling للتشغيل على Replit
        logger.info("تم اكتشاف بيئة Replit، استخدام polling للتشغيل...")
        application.run_polling()
    elif app_url:
        # استخدام webhook للنشر على منصات سحابية
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=f"{app_url}/{BOT_TOKEN}"
        )
        logger.info(f"تم بدء البوت باستخدام webhook على المنفذ {port}")
    else:
        # استخدام polling للتطوير المحلي
        application.run_polling()
        logger.info("تم بدء البوت باستخدام polling")

if __name__ == "__main__":
    main()