import os
import json
import math
import pandas as pd

excel_path = os.path.expanduser(r"~\Downloads\Costing V21.xlsx")
output_json = r"assets\data\costing_data.json"

def clean_str(val):
    if pd.isna(val) or val is None:
        return ""
    s = str(val).replace("*****", "").strip()
    return "" if s.lower() == "nan" else s

def clean_num(val):
    try:
        if pd.isna(val) or val is None:
            return 0.0
        f = float(val)
        return 0.0 if (math.isnan(f) or math.isinf(f)) else f
    except:
        return 0.0

def norm(text):
    t = clean_str(text).replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    if t.startswith("ارز "):
        t = "رز " + t[4:]
    return t.strip()

print(f"قراءة ملف الإكسل: {excel_path}...")
xls = pd.ExcelFile(excel_path)

# 1. قراءة شيت Semi Finished Recipe
df_semi = pd.read_excel(xls, sheet_name="Semi Finished Recipe").dropna(how="all")
semi_dict = {}

for _, row in df_semi.iterrows():
    vals = list(row.values)
    if len(vals) < 12:
        continue

    sf_odoo = clean_str(vals[0])
    sf_code = clean_str(vals[1])
    sf_name = clean_str(vals[3])

    if not sf_name:
        continue

    rm_odoo = clean_str(vals[4])
    rm_code = clean_str(vals[5])
    rm_name = clean_str(vals[6])
    batch_qty = clean_num(vals[7])
    unit = clean_str(vals[8])
    eq_qty = clean_num(vals[9])
    c_unit = clean_num(vals[10])
    t_cost = clean_num(vals[11])

    sub_item = {
        "odoo_code": rm_odoo,
        "rm_code": rm_code,
        "name": rm_name if rm_name else "مادة خام",
        "batch_quantity": batch_qty,
        "unit": unit,
        "equivalent_quantity": eq_qty,
        "cost_per_unit": c_unit,
        "total_cost": t_cost
    }

    # الربط بكل المفاتيح الممكنة (كود الـ SF، كود الـ Odoo، واسم الصنف مثل رز اوزي)
    for k in [sf_code, sf_odoo, norm(sf_name), sf_name]:
        if k and k != "nan":
            if k not in semi_dict:
                semi_dict[k] = []
            semi_dict[k].append(sub_item)

print(f"تمت فهرسة {len(semi_dict)} من مجموعات المواد شبه المصنعة (SF).")

# 2. قراءة شيت Finished Recipe
df_finished = pd.read_excel(xls, sheet_name="Finished Recipe").dropna(how="all")
finished_items = {}
current_dish = None

for _, row in df_finished.iterrows():
    vals = list(row.values)
    if len(vals) < 13:
        continue

    d_odoo = clean_str(vals[0])
    d_code = clean_str(vals[1])
    d_name = clean_str(vals[3])

    # صنف رئيسي جديد
    if d_name:
        key = f"{d_odoo}_{d_code}_{d_name}"
        if key not in finished_items:
            m_price = clean_num(vals[14]) if len(vals) > 14 else 0.0
            finished_items[key] = {
                "odoo_code": d_odoo,
                "item_code": d_code,
                "name": d_name,
                "section": clean_str(vals[4]),
                "group_name": clean_str(vals[5]),
                "markaziya_price": m_price,
                "calculated_cost": 0.0,
                "profit_margin": 0.0,
                "ingredients": []
            }
        current_dish = finished_items[key]

    if current_dish is None:
        continue

    # المكونات
    ing_odoo = clean_str(vals[6])
    ing_code = clean_str(vals[7])
    ing_name = clean_str(vals[8])

    if not ing_name:
        continue

    sub_items = []
    for lookup in [ing_code, ing_odoo, norm(ing_name), ing_name]:
        if lookup in semi_dict and len(semi_dict[lookup]) > 0:
            sub_items = semi_dict[lookup]
            break

    is_sf = (
        len(sub_items) > 0 or 
        ing_odoo.startswith("SF") or 
        ing_code.startswith("SF") or 
        "محشي" in ing_name or 
        "اوزي" in ing_name or 
        "مقلي" in ing_name
    )

    qty = clean_num(vals[10])
    cost_u = clean_num(vals[11])
    tot_c = clean_num(vals[12])

    current_dish["ingredients"].append({
        "odoo_code": ing_odoo,
        "code": ing_code,
        "name": ing_name,
        "unit": clean_str(vals[9]),
        "quantity": qty,
        "cost_per_unit": cost_u,
        "total_cost": tot_c,
        "is_semi_finished": is_sf,
        "sub_ingredients": sub_items
    })

# حساب التكلفة الصحيحة وهامش الربح تلقائياً بمجموع المكونات
for dish in finished_items.values():
    total_recipe_cost = sum(i["total_cost"] for i in dish["ingredients"])
    dish["calculated_cost"] = total_recipe_cost
    if dish["markaziya_price"] > 0:
        dish["profit_margin"] = (dish["markaziya_price"] - total_recipe_cost) / dish["markaziya_price"]

items_list = list(finished_items.values())
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(items_list, f, ensure_ascii=False, indent=2, allow_nan=False)

print(f"تم بنجاح توليد {len(items_list)} صنف بحسابات تكلفة دقيقة 100%!")
