import json
import os
import pandas as pd
from config import DATABASE_FILE

# التأكد من وجود ملف البيانات
def ensure_data_file_exists():
    """التأكد من وجود ملف البيانات وإنشائه إذا لم يكن موجوداً"""
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'expenses': [],
                'income': [],
                'categories': ['طعام', 'مواصلات', 'سكن', 'ترفيه', 'أخرى']
            }, f, ensure_ascii=False, indent=4)

# إضافة مصروف جديد
def add_expense(amount, category, description, date):
    """إضافة مصروف جديد إلى قاعدة البيانات"""
    ensure_data_file_exists()
    
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    expense = {
        'amount': float(amount),
        'category': category,
        'description': description,
        'date': date
    }
    
    data['expenses'].append(expense)
    
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return True

# إضافة دخل جديد
def add_income(amount, source, description, date):
    """إضافة دخل جديد إلى قاعدة البيانات"""
    ensure_data_file_exists()
    
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    income = {
        'amount': float(amount),
        'source': source,
        'description': description,
        'date': date
    }
    
    data['income'].append(income)
    
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return True

# الحصول على ملخص المصروفات
def get_expenses_summary():
    """الحصول على ملخص المصروفات حسب الفئة"""
    ensure_data_file_exists()
    
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data['expenses']:
        return "لا توجد مصروفات مسجلة بعد."
    
    df = pd.DataFrame(data['expenses'])
    summary = df.groupby('category')['amount'].sum().reset_index()
    
    result = "📊 ملخص المصروفات:\n\n"
    total = 0
    
    for _, row in summary.iterrows():
        result += f"🔹 {row['category']}: {row['amount']}\n"
        total += row['amount']
    
    result += f"\n💰 إجمالي المصروفات: {total}"
    return result

# الحصول على ملخص الدخل
def get_income_summary():
    """الحصول على ملخص الدخل"""
    ensure_data_file_exists()
    
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data['income']:
        return "لا يوجد دخل مسجل بعد."
    
    df = pd.DataFrame(data['income'])
    total = df['amount'].sum()
    
    result = "📈 ملخص الدخل:\n\n"
    for _, row in df.iterrows():
        result += f"🔹 {row['date']} - {row['source']}: {row['amount']} ({row['description']})\n"
    
    result += f"\n💰 إجمالي الدخل: {total}"
    return result

# الحصول على الرصيد الحالي
def get_balance():
    """حساب الرصيد الحالي (الدخل - المصروفات)"""
    ensure_data_file_exists()
    
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_income = sum(item['amount'] for item in data['income'])
    total_expenses = sum(item['amount'] for item in data['expenses'])
    
    balance = total_income - total_expenses
    
    return f"💵 الرصيد الحالي: {balance}\n\n📥 إجمالي الدخل: {total_income}\n📤 إجمالي المصروفات: {total_expenses}"