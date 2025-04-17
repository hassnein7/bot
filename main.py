import logging
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from config import BOT_TOKEN
import utils
from accounting_knowledge import get_accounting_info, get_accounting_topics
from report_analysis import analyze_report, check_financial_statements

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
    logger.debug(f"تم استلام أمر analyze_report من المستخدم: {update.effective_user.id}")
    context.user_data['state'] = STATE_ANALYZING_REPORT
    context.user_data['temp_data'] = {}
    
    await update.message.reply_text(
        "📊 تحليل تقرير مالي\n\n"
        "الرجاء إرسال نص التقرير المالي الذي ترغب في تحليله:"
    )
    logger.debug("تم إرسال طلب إدخال التقرير المالي بنجاح")

# وظيفة تحليل القوائم المالية
async def analyze_statements_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية تحليل القوائم المالية"""
    logger.debug(f"تم استلام أمر analyze_statements من المستخدم: {update.effective_user.id}")
    context.user_data['state'] = STATE_ANALYZING_STATEMENTS
    context.user_data['temp_data'] = {}
    
    await update.message.reply_text(
        "📑 تحليل القوائم المالية\n\n"
        "الرجاء إرسال قائمة المركز المالي (الميزانية) أولاً:"
    )
    logger.debug("تم إرسال طلب إدخال قائمة المركز المالي بنجاح")

# وظيفة عرض الملخص
# وظيفة عرض الملخص
async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض ملخص المصروفات والدخل"""
    logger.debug(f"تم استلام أمر summary من المستخدم: {update.effective_user.id}")
    expenses_summary = utils.get_expenses_summary()
    income_summary = utils.get_income_summary()
    
    await update.message.reply_text(f"{expenses_summary}\n\n{income_summary}")
    logger.debug("تم إرسال ملخص الحسابات بنجاح")

# وظيفة عرض الرصيد
# وظيفة عرض الرصيد
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الرصيد الحالي"""
    logger.debug(f"تم استلام أمر balance من المستخدم: {update.effective_user.id}")
    balance = utils.get_balance()
    await update.message.reply_text(balance)
    logger.debug("تم إرسال الرصيد الحالي بنجاح")

# معالجة الضغط على الأزرار
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الضغط على الأزرار"""
    logger.debug(f"تم استلام ضغطة زر من المستخدم: {update.effective_user.id}")
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("category_"):
        category = query.data.replace("category_", "")
        context.user_data['temp_data']['category'] = category
        logger.debug(f"تم اختيار الفئة: {category}")
        
        await query.edit_message_text(
            f"الفئة المختارة: {category}\n\n"
            "الرجاء إدخال مبلغ المصروف:"
        )
        logger.debug("تم إرسال رسالة إدخال المبلغ بنجاح")

# معالجة الرسائل النصية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل النصية حسب حالة المحادثة"""
    logger.debug(f"تم استلام رسالة نصية من المستخدم: {update.effective_user.id}, النص: {update.message.text[:20]}...")
    text = update.message.text
    state = context.user_data.get('state', STATE_NORMAL)
    
    if state == STATE_ANALYZING_REPORT:
        # تحليل التقرير المالي
        logger.debug("حالة تحليل التقرير المالي")
        report_text = text.strip()
        
        # تحليل التقرير
        analysis_result = analyze_financial_report(report_text)
        
        await update.message.reply_text(analysis_result)
        logger.debug("تم إرسال نتائج تحليل التقرير المالي بنجاح")
        
        # إعادة تعيين الحالة
        context.user_data['state'] = STATE_NORMAL
        context.user_data['temp_data'] = {}
    
    elif state == STATE_ANALYZING_STATEMENTS:
        # تحليل القوائم المالية
        temp_data = context.user_data.get('temp_data', {})
        logger.debug(f"حالة تحليل القوائم المالية، البيانات المؤقتة: {temp_data}")
        
        if 'balance_sheet' not in temp_data:
            temp_data['balance_sheet'] = text.strip()
            await update.message.reply_text(
                "تم استلام قائمة المركز المالي (الميزانية).\n\n"
                "الرجاء إدخال قائمة الدخل (الأرباح والخسائر):"
            )
            logger.debug("تم إرسال طلب إدخال قائمة الدخل بنجاح")
        
        elif 'balance_sheet' in temp_data and 'income_statement' not in temp_data:
            temp_data['income_statement'] = text.strip()
            
            # سؤال المستخدم إذا كان يريد إدخال قائمة التدفقات النقدية
            keyboard = [
                [InlineKeyboardButton("نعم", callback_data="cash_flow_yes")],
                [InlineKeyboardButton("لا", callback_data="cash_flow_no")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "تم استلام قائمة الدخل.\n\n"
                "هل تريد إدخال قائمة التدفقات النقدية؟",
                reply_markup=reply_markup
            )
            logger.debug("تم إرسال سؤال حول إدخال قائمة التدفقات النقدية بنجاح")
        
        elif 'balance_sheet' in temp_data and 'income_statement' in temp_data and 'cash_flow' not in temp_data and 'waiting_for_cash_flow' in temp_data and temp_data['waiting_for_cash_flow']:
            temp_data['cash_flow'] = text.strip()
            temp_data['waiting_for_cash_flow'] = False
            
            # تحليل القوائم المالية
            analysis_result = analyze_financial_statements(
                temp_data['balance_sheet'],
                temp_data['income_statement'],
                temp_data['cash_flow']
            )
            
            await update.message.reply_text(analysis_result)
            logger.debug("تم إرسال نتائج تحليل القوائم المالية بنجاح")
            
            # إعادة تعيين الحالة
            context.user_data['state'] = STATE_NORMAL
            context.user_data['temp_data'] = {}
    
    else:
        # حالة عادية - محاولة الإجابة على سؤال محاسبي
        logger.debug("حالة عادية، محاولة الإجابة على سؤال محاسبي")
        
        # البحث عن كلمات مفتاحية محاسبية في النص
        accounting_keywords = [
            "محاسبة", "محاسبي", "قيد", "دفتر", "ميزانية", "أصول", "خصوم", "التزامات", 
            "حقوق", "إيرادات", "مصروفات", "تكاليف", "ضرائب", "تدقيق", "مراجعة", 
            "قوائم مالية", "دخل", "مركز مالي", "تدفقات نقدية", "معايير", "IFRS", "IPSAS"
        ]
        
        # التحقق مما إذا كان النص يحتوي على كلمات مفتاحية محاسبية
        is_accounting_question = any(keyword in text.lower() for keyword in accounting_keywords)
        
        if is_accounting_question:
            # محاولة العثور على إجابة من قاعدة المعرفة
            # البحث عن أقرب موضوع في قاعدة المعرفة
            best_match = None
            best_match_score = 0
            
            for topic in accounting_info.keys():
                # حساب عدد الكلمات المشتركة بين السؤال والموضوع
                common_words = sum(1 for word in text.lower().split() if word in topic.lower())
                if common_words > best_match_score:
                    best_match_score = common_words
                    best_match = topic
            
            if best_match and best_match_score > 0:
                # إذا وجدنا موضوعاً مناسباً، نقدم معلومات عنه
                info = get_accounting_info(best_match)
                await update.message.reply_text(
                    f"أعتقد أنك تسأل عن {best_match}:\n\n{info}\n\n"
                    "هل تريد معرفة المزيد؟ يمكنك استخدام الأمر /topics لعرض قائمة المواضيع المتاحة."
                )
            else:
                # إذا لم نجد موضوعاً مناسباً، نقدم رسالة عامة
                await update.message.reply_text(
                    "يبدو أنك تسأل عن موضوع محاسبي، لكنني لم أستطع تحديد الموضوع بدقة.\n\n"
                    "يمكنك استخدام الأمر /topics لعرض قائمة المواضيع المحاسبية المتاحة، "
                    "أو استخدام الأمر /info متبوعاً باسم الموضوع للحصول على معلومات تفصيلية.\n\n"
                    "مثال: /info مفهوم المحاسبة"
                )
        else:
            # إذا لم يكن السؤال متعلقاً بالمحاسبة، نقدم رسالة ترحيبية
            await update.message.reply_text(
                "مرحباً! أنا مساعدك المحاسبي الذكي. يمكنني مساعدتك في فهم المفاهيم المحاسبية وشرحها بطريقة مبسطة.\n\n"
                "استخدم الأوامر التالية:\n"
                "/topics - عرض قائمة المواضيع المحاسبية المتاحة\n"
                "/info [اسم الموضوع] - الحصول على معلومات حول موضوع محاسبي معين\n"
                "/help - عرض قائمة المساعدة\n\n"
                "أو يمكنك ببساطة أن تسألني أي سؤال محاسبي وسأحاول الإجابة عليه!"
            )
        
        logger.debug("تم إرسال الرد على رسالة المستخدم بنجاح")

# وظيفة عرض المواضيع المحاسبية
async def topics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المواضيع المحاسبية المتاحة"""
    logger.debug(f"تم استلام أمر topics من المستخدم: {update.effective_user.id}")
    topics_list = get_accounting_topics()
    await update.message.reply_text(topics_list)
    logger.debug("تم إرسال قائمة المواضيع المحاسبية بنجاح")

# وظيفة عرض معلومات حول موضوع محاسبي معين
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات حول موضوع محاسبي معين"""
    logger.debug(f"تم استلام أمر info من المستخدم: {update.effective_user.id}")
    
    if not context.args:
        await update.message.reply_text(
            "الرجاء تحديد اسم الموضوع المحاسبي.\n"
            "مثال: /info مفهوم المحاسبة\n\n"
            "استخدم الأمر /topics لعرض قائمة المواضيع المتاحة."
        )
        return
    
    topic = " ".join(context.args)
    info = get_accounting_info(topic)
    await update.message.reply_text(info)
    logger.debug(f"تم إرسال معلومات حول الموضوع: {topic}")

# وظيفة عرض المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المساعدة"""
    logger.debug(f"تم استلام أمر help من المستخدم: {update.effective_user.id}")
    
    await update.message.reply_text(
        "🔍 قائمة المساعدة:\n\n"
        "أنا مساعدك المحاسبي الذكي، وهذه هي الأوامر التي يمكنك استخدامها:\n\n"
        "/start - بدء محادثة جديدة مع البوت\n"
        "/topics - عرض قائمة المواضيع المحاسبية المتاحة\n"
        "/info [اسم الموضوع] - الحصول على معلومات حول موضوع محاسبي معين\n"
        "/analyze_report - تحليل تقرير مالي وتقديم ملاحظات وتوصيات\n"
        "/analyze_statements - تحليل القوائم المالية (الميزانية، قائمة الدخل، التدفقات النقدية)\n"
        "/help - عرض هذه القائمة\n\n"
        "يمكنك أيضاً أن تسألني مباشرة عن أي موضوع محاسبي وسأحاول مساعدتك!\n"
        "أو يمكنك إرسال تقارير مالية لي لفحصها وتحليلها وتقديم ملاحظات وتوصيات عليها."
    )
    logger.debug("تم إرسال قائمة المساعدة بنجاح")

# الدالة الرئيسية
def main():
    """تشغيل البوت"""
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("topics", topics_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze_report", analyze_report_command))
    application.add_handler(CommandHandler("analyze_statements", analyze_statements_command))
    
    # إضافة معالج الأزرار
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # إضافة معالج الرسائل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # تشغيل البوت
    # استخدام webhook للتوافق مع منصة Render إذا كان متغير PORT موجوداً
    port = int(os.environ.get("PORT", 8443))
    app_url = os.environ.get("APP_URL", "")
    
    if app_url:
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