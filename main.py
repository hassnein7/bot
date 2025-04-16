import logging
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from config import BOT_TOKEN
import utils

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # تغيير مستوى التسجيل من INFO إلى DEBUG للحصول على معلومات أكثر تفصيلاً
)

logger = logging.getLogger(__name__)
# حالات المحادثة
STATE_NORMAL = 0
STATE_ADDING_EXPENSE = 1
STATE_ADDING_INCOME = 2

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
        "أنا بوت المحاسبة الشخصية. يمكنني مساعدتك في تتبع مصروفاتك ودخلك.\n\n"
        "استخدم الأوامر التالية:\n"
        "/expense - إضافة مصروف جديد\n"
        "/income - إضافة دخل جديد\n"
        "/summary - عرض ملخص الحسابات\n"
        "/balance - عرض الرصيد الحالي"
    )

# وظيفة إضافة مصروف
# وظيفة إضافة مصروف
async def expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية إضافة مصروف جديد"""
    logger.debug(f"تم استلام أمر expense من المستخدم: {update.effective_user.id}")
    context.user_data['state'] = STATE_ADDING_EXPENSE
    context.user_data['temp_data'] = {}
    
    # إنشاء لوحة مفاتيح للفئات
    utils.ensure_data_file_exists()
    keyboard = []
    categories = ['طعام', 'مواصلات', 'سكن', 'ترفيه', 'أخرى']
    
    for category in categories:
        keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🛒 إضافة مصروف جديد\n\n"
        "الرجاء اختيار فئة المصروف:",
        reply_markup=reply_markup
    )
    logger.debug("تم إرسال رسالة اختيار فئة المصروف بنجاح")

# وظيفة إضافة دخل
# وظيفة إضافة دخل
async def income_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية إضافة دخل جديد"""
    logger.debug(f"تم استلام أمر income من المستخدم: {update.effective_user.id}")
    context.user_data['state'] = STATE_ADDING_INCOME
    context.user_data['temp_data'] = {}
    
    await update.message.reply_text(
        "💰 إضافة دخل جديد\n\n"
        "الرجاء إدخال مصدر الدخل (مثال: راتب، مبيعات، إلخ):"
    )
    logger.debug("تم إرسال رسالة إدخال مصدر الدخل بنجاح")

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
    
    if state == STATE_ADDING_EXPENSE:
        # إضافة مصروف جديد
        temp_data = context.user_data.get('temp_data', {})
        logger.debug(f"حالة إضافة مصروف، البيانات المؤقتة: {temp_data}")
        
        if 'category' in temp_data and 'amount' not in temp_data:
            try:
                amount = float(text.strip())
                temp_data['amount'] = amount
                await update.message.reply_text(
                    f"المبلغ: {amount}\n\n"
                    "الرجاء إدخال وصف للمصروف:"
                )
                logger.debug("تم إرسال رسالة إدخال الوصف بنجاح")
            except ValueError:
                await update.message.reply_text("الرجاء إدخال رقم صحيح للمبلغ.")
                logger.debug("خطأ في إدخال المبلغ")
        
        elif 'category' in temp_data and 'amount' in temp_data and 'description' not in temp_data:
            temp_data['description'] = text.strip()
            temp_data['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            logger.debug("تم استلام وصف المصروف، جاري الحفظ")
            
            # حفظ المصروف
            utils.add_expense(
                temp_data['amount'],
                temp_data['category'],
                temp_data['description'],
                temp_data['date']
            )
            
            await update.message.reply_text(
                "✅ تم إضافة المصروف بنجاح!\n\n"
                f"الفئة: {temp_data['category']}\n"
                f"المبلغ: {temp_data['amount']}\n"
                f"الوصف: {temp_data['description']}\n"
                f"التاريخ: {temp_data['date']}"
            )
            logger.debug("تم إضافة المصروف بنجاح وإرسال رسالة التأكيد")
            
            # إعادة تعيين الحالة
            context.user_data['state'] = STATE_NORMAL
            context.user_data['temp_data'] = {}
    
    elif state == STATE_ADDING_INCOME:
        # إضافة دخل جديد
        temp_data = context.user_data.get('temp_data', {})
        logger.debug(f"حالة إضافة دخل، البيانات المؤقتة: {temp_data}")
        
        if 'source' not in temp_data:
            temp_data['source'] = text.strip()
            await update.message.reply_text(
                f"المصدر: {temp_data['source']}\n\n"
                "الرجاء إدخال مبلغ الدخل:"
            )
            logger.debug("تم إرسال رسالة إدخال المبلغ بنجاح")
        
        elif 'source' in temp_data and 'amount' not in temp_data:
            try:
                amount = float(text.strip())
                temp_data['amount'] = amount
                await update.message.reply_text(
                    f"المبلغ: {amount}\n\n"
                    "الرجاء إدخال وصف للدخل:"
                )
                logger.debug("تم إرسال رسالة إدخال الوصف بنجاح")
            except ValueError:
                await update.message.reply_text("الرجاء إدخال رقم صحيح للمبلغ.")
                logger.debug("خطأ في إدخال المبلغ")
        
        elif 'source' in temp_data and 'amount' in temp_data and 'description' not in temp_data:
            temp_data['description'] = text.strip()
            temp_data['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            logger.debug("تم استلام وصف الدخل، جاري الحفظ")
            
            # حفظ الدخل
            utils.add_income(
                temp_data['amount'],
                temp_data['source'],
                temp_data['description'],
                temp_data['date']
            )
            
            await update.message.reply_text(
                "✅ تم إضافة الدخل بنجاح!\n\n"
                f"المصدر: {temp_data['source']}\n"
                f"المبلغ: {temp_data['amount']}\n"
                f"الوصف: {temp_data['description']}\n"
                f"التاريخ: {temp_data['date']}"
            )
            logger.debug("تم إضافة الدخل بنجاح وإرسال رسالة التأكيد")
            
            # إعادة تعيين الحالة
            context.user_data['state'] = STATE_NORMAL
            context.user_data['temp_data'] = {}
    
    else:
        # حالة عادية - إرسال رسالة مساعدة
        logger.debug("حالة عادية، إرسال رسالة المساعدة")
        await update.message.reply_text(
            "استخدم الأوامر التالية:\n"
            "/expense - إضافة مصروف جديد\n"
            "/income - إضافة دخل جديد\n"
            "/summary - عرض ملخص الحسابات\n"
            "/balance - عرض الرصيد الحالي"
        )
        logger.debug("تم إرسال رسالة المساعدة بنجاح")

# الدالة الرئيسية
def main():
    """تشغيل البوت"""
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("expense", expense_command))
    application.add_handler(CommandHandler("income", income_command))
    application.add_handler(CommandHandler("summary", summary_command))
    application.add_handler(CommandHandler("balance", balance_command))
    
    # إضافة معالج الأزرار
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # إضافة معالج الرسائل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # تشغيل البوت
    application.run_polling()

if __name__ == "__main__":
    main()