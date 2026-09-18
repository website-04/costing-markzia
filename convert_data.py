import pandas as pd
import json

def safe_str(val):
    if pd.isna(val): return ""
    return str(val).strip()

def safe_float(val):
    if pd.isna(val): return 0.0
    try:
        return float(val)
    except:
        return 0.0

# تحديد مسار ملف الإكسل
file_path = "Costing V21.xlsx"
print("جاري قراءة ملف الإكسل، يرجى الانتظار...")

try:
    # قراءة الشيتات
    df_finished = pd.read_excel(file_path, sheet_name='Finished Recipe')
    df_semi = pd.read_excel(file_path, sheet_name='Semi Finished Recipe')

    database = {}

    # معالجة المنتجات النهائية (Finished Recipes)
    for index, row in df_finished.iterrows():
        parent_code = safe_str(row.get('odoo'))
        if not parent_code:
            parent_code = safe_str(row.get('Menu Item\nNew Code'))
        
        if not parent_code: continue

        if parent_code not in database:
            database[parent_code] = {
                "name": safe_str(row.get('Menu Item\nName')),
                "type": "Finished",
                "total_cost": safe_float(row.get('تكلفة الصنف')),
                "ingredients": []
            }
            
        ing_code = safe_str(row.get('odoo.1'))
        if not ing_code:
            ing_code = safe_str(row.get('RM Item\nNew Code'))
            
        database[parent_code]['ingredients'].append({
            "code": ing_code,
            "name": safe_str(row.get('Complete Item Description')),
            "quantity": safe_float(row.get('Quantity')),
            "unit": safe_str(row.get('Unit')),
            "cost_per_unit": safe_float(row.get('Cost per Unit')),
            "total_cost": safe_float(row.get('Total Cost'))
        })

    # معالجة المنتجات شبه المصنعة (Semi Finished Recipes)
    for index, row in df_semi.iterrows():
        parent_code = safe_str(row.get('odoo'))
        if not parent_code:
            parent_code = safe_str(row.get('SF Item\nCode'))
            
        if not parent_code: continue

        if parent_code not in database:
            database[parent_code] = {
                "name": safe_str(row.get('SF Item\nName')),
                "type": "Semi-Finished",
                "ingredients": []
            }
            
        ing_code = safe_str(row.get('odoo.1'))
        if not ing_code:
            ing_code = safe_str(row.get('RM Item\nNew Code'))
            
        database[parent_code]['ingredients'].append({
            "code": ing_code,
            "name": safe_str(row.get('Complete Item Description')),
            "quantity": safe_float(row.get('الكمية المعادلة')),
            "unit": safe_str(row.get('Unit')),
            "cost_per_unit": safe_float(row.get('Cost Per Unit')),
            "total_cost": safe_float(row.get('Total Cost'))
        })

    # تصدير البيانات إلى ملف JSON
    output_file = 'recipes_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=4)

    print(f"تم بنجاح! تم استخراج البيانات وحفظها في ملف {output_file}")

except FileNotFoundError:
    print(f"خطأ: لم يتم العثور على ملف {file_path}. تأكد من وجوده في نفس المجلد.")
except Exception as e:
    print(f"حدث خطأ غير متوقع: {e}")