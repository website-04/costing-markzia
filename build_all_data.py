import os
import json
import math
import shutil
import pandas as pd

# مسارات الملفات
p_costing = os.path.expanduser(r"~\Downloads\Costing V21.xlsx")
if not os.path.exists(p_costing): p_costing = "Costing V21.xlsx"

p_staff = os.path.expanduser(r"~\Desktop\ريسبي وجبات الموظفين.xlsx")
p_odoo = os.path.expanduser(r"~\Downloads\اصناف اودو اخر تحديث (2).xlsx")
p_talabat = os.path.expanduser(r"~\Downloads\طلبات مارت نهائي (3).xlsx")
p_logo = os.path.expanduser(r"~\Desktop\شعار-المركزية4-1.png")

out_dir = os.path.join("assets", "data")
os.makedirs(out_dir, exist_ok=True)
os.makedirs("assets", exist_ok=True)

# نسخ الشعار تلقائياً إلى مجلد الأصول والويب
if os.path.exists(p_logo):
    shutil.copy(p_logo, os.path.join("assets", "logo.png"))
    if os.path.exists("web"):
        shutil.copy(p_logo, os.path.join("web", "favicon.png"))
    print("✅ تم نسخ شعار المركزية بنجاح إلى أصول التطبيق.")

def c_str(v):
    if pd.isna(v) or v is None: return ""
    s = str(v).replace("*****", "").strip()
    return "" if s.lower() == "nan" else s

def c_num(v):
    try:
        if pd.isna(v) or v is None: return 0.0
        f = float(v)
        return 0.0 if (math.isnan(f) or math.isinf(f)) else f
    except:
        return 0.0

def norm(text):
    t = c_str(text).replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    if t.startswith("ارز "): t = "رز " + t[4:]
    return t.strip().lower()

def find_col(df, keys):
    for col in df.columns:
        c = str(col).lower().replace("\n", " ").strip()
        if any(k in c for k in keys):
            return col
    return None

# ==========================================
# 1. قراءة دليل أصناف أودو (Odoo Catalog)
# ==========================================
odoo_items = []
odoo_map_by_code = {}
odoo_map_by_name = {}

if os.path.exists(p_odoo):
    print(f"جاري قراءة دليل أودو من: {p_odoo}...")
    df_odoo = pd.read_excel(p_odoo).dropna(how="all")
    
    name_col = find_col(df_odoo, ["اسم", "name", "description", "صنف", "منتج"]) or df_odoo.columns[0]
    code_col = find_col(df_odoo, ["مرجع", "reference", "كود", "code", "رمز", "default_code"])
    cat_col = find_col(df_odoo, ["فئة", "category", "قسم", "نوع"])
    cost_col = find_col(df_odoo, ["تكلفة", "cost", "standard_price"])
    price_col = find_col(df_odoo, ["بيع", "price", "سعر", "list_price"])
    unit_col = find_col(df_odoo, ["وحدة", "unit", "uom"])
    barcode_col = find_col(df_odoo, ["بار", "barcode"])

    for _, row in df_odoo.iterrows():
        name = c_str(row.get(name_col))
        if not name: continue
        code = c_str(row.get(code_col)) if code_col else ""
        cat = c_str(row.get(cat_col)) if cat_col else "عام"
        cost = c_num(row.get(cost_col)) if cost_col else 0.0
        price = c_num(row.get(price_col)) if price_col else 0.0
        unit = c_str(row.get(unit_col)) if unit_col else "قطعة"
        barcode = c_str(row.get(barcode_col)) if barcode_col else ""

        item_obj = {
            "code": code,
            "name": name,
            "category": cat,
            "cost": cost,
            "price": price,
            "unit": unit,
            "barcode": barcode
        }
        odoo_items.append(item_obj)
        if code: odoo_map_by_code[code.lower()] = item_obj
        if barcode: odoo_map_by_code[barcode.lower()] = item_obj
        odoo_map_by_name[norm(name)] = item_obj

    print(f"تمت فهرسة {len(odoo_items)} صنف من أودو.")

with open(os.path.join(out_dir, "odoo_catalog.json"), "w", encoding="utf-8") as f:
    json.dump(odoo_items, f, ensure_ascii=False, indent=2, allow_nan=False)

# ==========================================
# 2. قراءة شجرة التكاليف وقواعد RM & SF
# ==========================================
semi_dict = {}
rm_sf_master = {}

if os.path.exists(p_costing):
    print(f"جاري قراءة شجرة التكاليف الرئيسية: {p_costing}...")
    xls_c = pd.ExcelFile(p_costing)

    # فحص شيتات RM & SF العامة
    for s_name in xls_c.sheet_names:
        s_low = s_name.lower()
        if ("rm" in s_low and "sf" in s_low) or "master" in s_low:
            print(f"جاري استخراج بيانات شيت {s_name}...")
            df_rm = pd.read_excel(xls_c, sheet_name=s_name).dropna(how="all")
            r_code_col = find_col(df_rm, ["كود", "code", "مرجع", "odoo"])
            r_name_col = find_col(df_rm, ["اسم", "name", "description", "مادة"])
            r_unit_col = find_col(df_rm, ["وحدة", "unit"])
            r_cost_col = find_col(df_rm, ["كلفة", "cost", "سعر"])
            r_type_col = find_col(df_rm, ["نوع", "type"])
            for _, r_row in df_rm.iterrows():
                rc = c_str(r_row.get(r_code_col)) if r_code_col else ""
                rn = c_str(r_row.get(r_name_col)) if r_name_col else ""
                if not rc and not rn: continue
                m_obj = {
                    "code": rc,
                    "name": rn,
                    "unit": c_str(r_row.get(r_unit_col)) if r_unit_col else "",
                    "cost": c_num(r_row.get(r_cost_col)) if r_cost_col else 0.0,
                    "type": c_str(r_row.get(r_type_col)) if r_type_col else "RM/SF",
                    "sheet": s_name
                }
                if rc: rm_sf_master[rc.lower()] = m_obj
                if rn: rm_sf_master[norm(rn)] = m_obj

    # قراءة شيت Semi Finished Recipe
    df_semi = pd.read_excel(xls_c, sheet_name="Semi Finished Recipe").dropna(how="all")
    current_sf_odoo = ""
    current_sf_code = ""
    current_sf_name = ""

    for _, row in df_semi.iterrows():
        vals = list(row.values)
        if len(vals) < 12: continue

        if c_str(vals[3]):
            current_sf_odoo = c_str(vals[0])
            current_sf_code = c_str(vals[1])
            current_sf_name = c_str(vals[3])

        if not current_sf_name: continue

        sub_item = {
            "odoo_code": c_str(vals[4]),
            "rm_code": c_str(vals[5]),
            "name": c_str(vals[6]) or "مادة خام",
            "batch_quantity": c_num(vals[7]),
            "unit": c_str(vals[8]),
            "equivalent_quantity": c_num(vals[9]),
            "cost_per_unit": c_num(vals[10]),
            "total_cost": c_num(vals[11])
        }
        for k in [current_sf_code, current_sf_odoo, norm(current_sf_name), current_sf_name]:
            if k and k != "nan":
                k_low = k.lower()
                if k_low not in semi_dict: semi_dict[k_low] = []
                semi_dict[k_low].append(sub_item)

    # قراءة Finished Recipe
    df_finished = pd.read_excel(xls_c, sheet_name="Finished Recipe").dropna(how="all")
    finished_items = {}
    current_dish = None

    for _, row in df_finished.iterrows():
        vals = list(row.values)
        if len(vals) < 13: continue
        d_odoo = c_str(vals[0])
        d_code = c_str(vals[1])
        d_name = c_str(vals[3])

        if d_name:
            key = f"{d_odoo}_{d_code}_{d_name}"
            if key not in finished_items:
                m_price = c_num(vals[14]) if len(vals) > 14 else 0.0
                finished_items[key] = {
                    "odoo_code": d_odoo,
                    "item_code": d_code,
                    "name": d_name,
                    "section": c_str(vals[4]),
                    "group_name": c_str(vals[5]),
                    "markaziya_price": m_price,
                    "calculated_cost": 0.0,
                    "profit_margin": 0.0,
                    "ingredients": []
                }
            current_dish = finished_items[key]

        if current_dish is None: continue

        ing_odoo = c_str(vals[6])
        ing_code = c_str(vals[7])
        ing_name = c_str(vals[8])
        if not ing_name: continue

        subs = []
        for lookup in [ing_code.lower(), ing_odoo.lower(), norm(ing_name)]:
            if lookup in semi_dict and len(semi_dict[lookup]) > 0:
                subs = semi_dict[lookup]
                break

        is_sf = len(subs) > 0 or ing_odoo.startswith("SF") or ing_code.startswith("SF")

        current_dish["ingredients"].append({
            "odoo_code": ing_odoo,
            "code": ing_code,
            "name": ing_name,
            "unit": c_str(vals[9]),
            "quantity": c_num(vals[10]),
            "cost_per_unit": c_num(vals[11]),
            "total_cost": c_num(vals[12]),
            "is_semi_finished": is_sf,
            "sub_ingredients": subs
        })

    for dish in finished_items.values():
        tot = sum(i["total_cost"] for i in dish["ingredients"])
        dish["calculated_cost"] = tot
        if dish["markaziya_price"] > 0:
            dish["profit_margin"] = (dish["markaziya_price"] - tot) / dish["markaziya_price"]

    c_list = list(finished_items.values())
    with open(os.path.join(out_dir, "costing_data.json"), "w", encoding="utf-8") as f:
        json.dump(c_list, f, ensure_ascii=False, indent=2, allow_nan=False)
    print(f"تم استخراج {len(c_list)} صنف في شجرة التكاليف.")

# ==========================================
# 3. معالجة وجبات الموظفين الذكية (بالتواريخ وربط أودو)
# ==========================================
staff_meals = []
if os.path.exists(p_staff):
    print(f"جاري قراءة ريسبي وجبات الموظفين الذكي من: {p_staff}...")
    xls_staff = pd.ExcelFile(p_staff)
    meals_dict = {}

    for s_name in xls_staff.sheet_names:
        df_s = pd.read_excel(xls_staff, sheet_name=s_name).dropna(how="all")

        col_date = find_col(df_s, ["تاريخ", "date"]) or df_s.columns[0]
        col_code = find_col(df_s, ["كود", "code"]) or df_s.columns[1]
        col_meal = find_col(df_s, ["اسم الوجبه", "اسم الوجبة", "meal"]) or df_s.columns[2]
        col_raw = find_col(df_s, ["رسبي", "وصفة", "recipe"]) or df_s.columns[3]
        col_qty = find_col(df_s, ["كمية رسبي", "كمية"]) or df_s.columns[4]
        col_kg = find_col(df_s, ["بالكيلو", "كيلو"]) or df_s.columns[5]
        col_cost = find_col(df_s, ["الكلفة", "سعر"]) or df_s.columns[6]
        col_tot = find_col(df_s, ["اجمالي", "إجمالي"]) or df_s.columns[7]

        for _, row in df_s.iterrows():
            raw_date = row.get(col_date)
            date_str = ""
            if pd.notna(raw_date):
                try:
                    date_str = pd.to_datetime(raw_date).strftime("%Y-%m-%d")
                except:
                    date_str = c_str(raw_date)

            meal_name = c_str(row.get(col_meal))
            if not meal_name: continue

            ing_code = c_str(row.get(col_code))
            raw_desc = c_str(row.get(col_raw))

            # البحث الذكي عن الاسم الرسمي في أودو باستخدام كود الصنف (Column B)
            clean_name = ""
            if ing_code:
                odoo_match = odoo_map_by_code.get(ing_code.lower())
                if odoo_match:
                    clean_name = odoo_match.get("name", "")
                elif ing_code.lower() in rm_sf_master:
                    clean_name = rm_sf_master[ing_code.lower()].get("name", "")

            # إذا لم يوجد في أودو، نستخدم الوصف من عامود D كاحتياط
            if not clean_name:
                clean_name = raw_desc or f"صنف {ing_code}"

            qty_g = c_num(row.get(col_qty))
            qty_kg = c_num(row.get(col_kg))
            cost_u = c_num(row.get(col_cost))
            tot_c = c_num(row.get(col_tot))

            if tot_c == 0.0 and cost_u > 0:
                tot_c = cost_u * (qty_kg if qty_kg > 0 else (qty_g / 1000.0 if qty_g > 0 else 1.0))

            qty_val = qty_kg if qty_kg > 0 else qty_g
            unit_val = "كيلو" if qty_kg > 0 else "غم"

            # فحص إذا كان الصنف في وجبة الموظف نصف مصنع له تفريعات
            subs = []
            if ing_code.lower() in semi_dict:
                subs = semi_dict[ing_code.lower()]
            elif norm(clean_name) in semi_dict:
                subs = semi_dict[norm(clean_name)]

            # تجميع بالاسم والتاريخ لتمييز كل يوم
            group_key = f"{meal_name}____{date_str}"
            if group_key not in meals_dict:
                meals_dict[group_key] = {
                    "name": meal_name,
                    "date": date_str if date_str else "تاريخ غير محدد",
                    "code": f"STAFF-{len(meals_dict)+1:03d}",
                    "total_cost": 0.0,
                    "ingredients": []
                }

            meals_dict[group_key]["ingredients"].append({
                "code": ing_code,
                "name": clean_name,
                "raw_description": raw_desc,
                "quantity": qty_val,
                "unit": unit_val,
                "cost_per_unit": cost_u,
                "total_cost": tot_c,
                "is_semi_finished": len(subs) > 0 or ing_code.startswith("SF"),
                "sub_ingredients": subs
            })

    for m in meals_dict.values():
        m["total_cost"] = sum(i["total_cost"] for i in m["ingredients"])
        staff_meals.append(m)

    print(f"تم بنجاح تجميع {len(staff_meals)} وجبة موظفين بالتواريخ والأسماء الرسمية.")

with open(os.path.join(out_dir, "staff_meals.json"), "w", encoding="utf-8") as f:
    json.dump(staff_meals, f, ensure_ascii=False, indent=2, allow_nan=False)

# ==========================================
# 4. قراءة طلبات مارت
# ==========================================
talabat_items = []
if os.path.exists(p_talabat):
    print(f"جاري قراءة طلبات مارت...")
    df_tal = pd.read_excel(p_talabat).dropna(how="all")
    t_name_col = find_col(df_tal, ["اسم", "name", "item"]) or df_tal.columns[0]
    t_code_col = find_col(df_tal, ["sku", "كود", "code"])
    t_barcode_col = find_col(df_tal, ["بار", "barcode"])
    t_price_col = find_col(df_tal, ["سعر", "price", "بيع"])
    t_cost_col = find_col(df_tal, ["تكلفة", "cost"])
    t_cat_col = find_col(df_tal, ["قسم", "فئة", "category"])

    for _, row in df_tal.iterrows():
        t_name = c_str(row.get(t_name_col))
        if not t_name: continue
        t_code = c_str(row.get(t_code_col)) if t_code_col else ""
        t_barcode = c_str(row.get(t_barcode_col)) if t_barcode_col else ""
        t_price = c_num(row.get(t_price_col)) if t_price_col else 0.0
        t_cost = c_num(row.get(t_cost_col)) if t_cost_col else 0.0
        t_cat = c_str(row.get(t_cat_col)) if t_cat_col else "عام"

        matched_odoo = odoo_map_by_code.get(t_barcode.lower()) or odoo_map_by_code.get(t_code.lower()) or odoo_map_by_name.get(norm(t_name))
        matched_odoo_code = ""
        if matched_odoo:
            matched_odoo_code = matched_odoo.get("code", "")
            if t_cost == 0.0: t_cost = matched_odoo.get("cost", 0.0)

        margin = ((t_price - t_cost) / t_price) if t_price > 0 else 0.0

        talabat_items.append({
            "name": t_name,
            "sku": t_code,
            "barcode": t_barcode,
            "category": t_cat,
            "price": t_price,
            "cost": t_cost,
            "margin": margin,
            "odoo_code": matched_odoo_code
        })

with open(os.path.join(out_dir, "talabat_mart.json"), "w", encoding="utf-8") as f:
    json.dump(talabat_items, f, ensure_ascii=False, indent=2, allow_nan=False)

print("🎉 اكتمل تحديث جميع قواعد البيانات الأربعة والشعار بنجاح!")