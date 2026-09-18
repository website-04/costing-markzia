import os
import json
import math
import shutil
import datetime
import pandas as pd

# المسارات المرشحة
p_costing_candidates = [
    "Costing V21.xlsx",
    os.path.expanduser(r"~\Downloads\Costing V21.xlsx"),
    r"C:\Users\NTC\Downloads\Costing V21.xlsx"
]
p_costing = next((p for p in p_costing_candidates if os.path.exists(p)), "Costing V21.xlsx")

p_staff_candidates = [
    r"C:\Users\NTC\Desktop\ريسبي وجبات الموظفين.xlsx",
    os.path.expanduser(r"~\Desktop\ريسبي وجبات الموظفين.xlsx"),
    os.path.expanduser(r"~\Downloads\ريسبي وجبات الموظفين.xlsx"),
]
p_staff = next((p for p in p_staff_candidates if os.path.exists(p)), None)

p_odoo_candidates = [
    os.path.expanduser(r"~\Downloads\اصناف اودو اخر تحديث (2).xlsx"),
    r"C:\Users\NTC\Downloads\اصناف اودو اخر تحديث (2).xlsx",
    os.path.expanduser(r"~\Desktop\اصناف اودو اخر تحديث (2).xlsx"),
]
p_odoo = next((p for p in p_odoo_candidates if os.path.exists(p)), None)

p_talabat_candidates = [
    r"C:\Users\NTC\Desktop\طلبات مارت نهائي (3).xlsx",
    os.path.expanduser(r"~\Desktop\طلبات مارت نهائي (3).xlsx"),
    os.path.expanduser(r"~\Downloads\طلبات مارت نهائي (3).xlsx"),
    r"C:\Users\NTC\Downloads\طلبات مارت نهائي (3).xlsx",
]
p_talabat = next((p for p in p_talabat_candidates if os.path.exists(p)), None)

out_dir = os.path.join("assets", "data")
os.makedirs(out_dir, exist_ok=True)
os.makedirs("assets", exist_ok=True)

def c_str(v):
    if pd.isna(v) or v is None: return ""
    s = str(v).replace("*****", "").strip()
    return "" if s.lower() in ["nan", "none"] else s

def c_num(v):
    try:
        if pd.isna(v) or v is None: return 0.0
        f = float(v)
        return 0.0 if (math.isnan(f) or math.isinf(f)) else f
    except:
        return 0.0

def norm(text):
    t = c_str(text).replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه")
    if t.startswith("ارز "): t = "رز " + t[4:]
    return t.strip().lower()

def find_col(df, inc_keys, exc_keys=[]):
    for col in df.columns:
        c = str(col).lower().replace("\n", " ").strip()
        if any(k in c for k in inc_keys):
            if not any(e in c for e in exc_keys):
                return col
    return None

# ==========================================
# 1. فهرسة دليل أودو الشامل
# ==========================================
odoo_items = []
odoo_map_by_code = {}
odoo_map_by_barcode = {}

if p_odoo and os.path.exists(p_odoo):
    print(f"قراءة دليل أودو من: {p_odoo}...")
    df_odoo = pd.read_excel(p_odoo).dropna(how="all")
    name_col = find_col(df_odoo, ["اسم", "name", "description", "صنف"]) or df_odoo.columns[0]
    code_col = find_col(df_odoo, ["مرجع", "reference", "كود", "code"])
    cat_col = find_col(df_odoo, ["فئة", "category", "قسم"])
    cost_col = find_col(df_odoo, ["تكلفة", "cost"])
    price_col = find_col(df_odoo, ["بيع", "price", "سعر"])
    unit_col = find_col(df_odoo, ["وحدة", "unit"])
    barcode_col = find_col(df_odoo, ["بار", "barcode"])

    for _, row in df_odoo.iterrows():
        name = c_str(row.get(name_col))
        if not name: continue
        code = c_str(row.get(code_col)) if code_col else ""
        barcode = c_str(row.get(barcode_col)) if barcode_col else ""
        item_obj = {
            "code": code,
            "name": name,
            "category": c_str(row.get(cat_col)) if cat_col else "عام",
            "cost": c_num(row.get(cost_col)) if cost_col else 0.0,
            "price": c_num(row.get(price_col)) if price_col else 0.0,
            "unit": c_str(row.get(unit_col)) if unit_col else "قطعة",
            "barcode": barcode
        }
        odoo_items.append(item_obj)
        if code: odoo_map_by_code[code.lower()] = item_obj
        if barcode: odoo_map_by_barcode[barcode.lower()] = item_obj

with open(os.path.join(out_dir, "odoo_catalog.json"), "w", encoding="utf-8") as f:
    json.dump(odoo_items, f, ensure_ascii=False, indent=2, allow_nan=False)
print(f"تم تصدير {len(odoo_items)} صنف من دليل أودو.")

# ==========================================
# 2. قراءة شجرة التكاليف BOM (Semi & Finished)
# ==========================================
semi_dict = {}
finished_items = {}

if p_costing and os.path.exists(p_costing):
    print(f"قراءة ملف التكاليف من: {p_costing}...")
    xls_c = pd.ExcelFile(p_costing)
    if "Semi Finished Recipe" in xls_c.sheet_names:
        df_semi = pd.read_excel(xls_c, sheet_name="Semi Finished Recipe").dropna(how="all")
        current_sf_code = ""
        current_sf_name = ""
        for _, row in df_semi.iterrows():
            vals = list(row.values)
            if len(vals) < 12: continue
            if c_str(vals[3]):
                current_sf_code = c_str(vals[1])
                current_sf_name = c_str(vals[3])
            if not current_sf_name: continue

            sub_item = {
                "rm_code": c_str(vals[5]),
                "name": c_str(vals[6]) or "مادة خام",
                "batch_quantity": c_num(vals[7]),
                "unit": c_str(vals[8]),
                "cost_per_unit": c_num(vals[10]),
                "total_cost": c_num(vals[11])
            }
            for k in [current_sf_code, norm(current_sf_name), current_sf_name]:
                if k:
                    k_low = k.lower()
                    if k_low not in semi_dict: semi_dict[k_low] = []
                    semi_dict[k_low].append(sub_item)

    if "Finished Recipe" in xls_c.sheet_names:
        df_finished = pd.read_excel(xls_c, sheet_name="Finished Recipe").dropna(how="all")
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
                        "odoo_code": d_odoo, "item_code": d_code, "name": d_name,
                        "section": c_str(vals[4]), "group_name": c_str(vals[5]),
                        "markaziya_price": m_price, "calculated_cost": 0.0, "profit_margin": 0.0,
                        "ingredients": []
                    }
                current_dish = finished_items[key]

            if current_dish is None: continue
            ing_code = c_str(vals[7])
            ing_name = c_str(vals[8])
            if not ing_name: continue

            subs = []
            for lookup in [ing_code.lower(), norm(ing_name)]:
                if lookup in semi_dict:
                    subs = semi_dict[lookup]
                    break

            current_dish["ingredients"].append({
                "code": ing_code, "name": ing_name,
                "unit": c_str(vals[9]), "quantity": c_num(vals[10]),
                "cost_per_unit": c_num(vals[11]), "total_cost": c_num(vals[12]),
                "is_semi_finished": len(subs) > 0 or ing_code.startswith("SF"),
                "sub_ingredients": subs
            })

        for dish in finished_items.values():
            tot = sum(i["total_cost"] for i in dish["ingredients"])
            dish["calculated_cost"] = tot
            if dish["markaziya_price"] > 0:
                dish["profit_margin"] = (dish["markaziya_price"] - tot) / dish["markaziya_price"]

with open(os.path.join(out_dir, "costing_data.json"), "w", encoding="utf-8") as f:
    json.dump(list(finished_items.values()), f, ensure_ascii=False, indent=2, allow_nan=False)
print(f"تم تصدير {len(finished_items)} وجبة رئيسية من شجرة التكاليف.")

# ==========================================
# 3. قراءة وجبات الموظفين وفصل التواريخ والأسماء بأودو
# ==========================================
staff_meals = []
if p_staff and os.path.exists(p_staff):
    print(f"قراءة ريسبي وجبات الموظفين من: {p_staff}...")
    xls_staff = pd.ExcelFile(p_staff)
    meals_dict = {}

    for s_name in xls_staff.sheet_names:
        df_raw = pd.read_excel(xls_staff, sheet_name=s_name, header=None)
        if len(df_raw) < 2: continue

        # البحث التلقائي عن صف العناوين
        header_row = 0
        found_hdr = False
        for r_idx in range(min(12, len(df_raw))):
            row_txt = " ".join([str(x) for x in df_raw.iloc[r_idx].values if pd.notna(x)]).lower()
            if any(k in row_txt for k in ["كود الصنف", "كود", "اسم الوجب", "رسبي", "كمية", "تاريخ"]):
                header_row = r_idx
                found_hdr = True
                break

        if found_hdr:
            df_s = pd.read_excel(xls_staff, sheet_name=s_name, skiprows=header_row).dropna(how="all")
        else:
            df_s = pd.read_excel(xls_staff, sheet_name=s_name).dropna(how="all")

        # مطابقة الأعمدة
        col_date = find_col(df_s, ["تاريخ", "date"])
        col_code = find_col(df_s, ["كود الصنف", "رمز الصنف", "كود", "code"], exc_keys=["وجب"])
        col_meal = find_col(df_s, ["اسم الوجبه", "اسم الوجبة", "الوجبة", "الوجبه", "meal"], exc_keys=["رسبي", "كمية"])
        col_raw = find_col(df_s, ["رسبي الوجبة", "رسبي الوجبه", "رسبي", "وصف", "المادة", "اسم المادة"], exc_keys=["كمية"])
        col_qty_g = find_col(df_s, ["كمية رسبي", "كمية"], exc_keys=["كيلو", "كلفة", "سعر"])
        col_qty_kg = find_col(df_s, ["بالكيلو", "كيلو"])
        col_cost = find_col(df_s, ["الكلفة", "كلفة", "سعر"], exc_keys=["اجمالي", "إجمالي"])
        col_tot = find_col(df_s, ["اجمالي", "إجمالي"])

        # بدائل بحسب موقع العمود في حال لم تطابق الأسماء
        cols_list = list(df_s.columns)
        if not col_date and len(cols_list) > 0: col_date = cols_list[0]
        if not col_code and len(cols_list) > 1: col_code = cols_list[1]
        if not col_meal and len(cols_list) > 2: col_meal = cols_list[2]
        if not col_raw and len(cols_list) > 3: col_raw = cols_list[3]
        if not col_qty_g and len(cols_list) > 4: col_qty_g = cols_list[4]
        if not col_qty_kg and len(cols_list) > 5: col_qty_kg = cols_list[5]
        if not col_cost and len(cols_list) > 6: col_cost = cols_list[6]
        if not col_tot and len(cols_list) > 7: col_tot = cols_list[7]

        # ملء التواريخ وأسماء الوجبات المدمجة
        if col_date and col_date in df_s: df_s[col_date] = df_s[col_date].ffill()
        if col_meal and col_meal in df_s: df_s[col_meal] = df_s[col_meal].ffill()

        for _, row in df_s.iterrows():
            meal_name = c_str(row.get(col_meal)) if col_meal else ""
            if not meal_name or meal_name.lower() in ["nan", "المجموع", "total"]: continue

            ing_code = c_str(row.get(col_code)) if col_code else ""
            raw_desc = c_str(row.get(col_raw)) if col_raw else ""

            # تجاهل صفوف المجاميع
            if not ing_code and not raw_desc: continue
            if any(k in raw_desc.lower() for k in ["مجموع", "المجموع", "total", "إجمالي"]): continue

            # استخراج وتنسيق التاريخ
            date_val = row.get(col_date) if col_date else None
            date_str = ""
            if pd.notna(date_val):
                try:
                    if isinstance(date_val, (pd.Timestamp, datetime.datetime, datetime.date)):
                        date_str = date_val.strftime("%Y-%m-%d")
                    else:
                        date_str = pd.to_datetime(str(date_val).strip(), dayfirst=True).strftime("%Y-%m-%d")
                except:
                    date_str = c_str(date_val).split(" ")[0]

            if not date_str or date_str.lower() in ["nan", "none"]:
                date_str = "تاريخ غير محدد"

            # الاسم الرسمي من دليل أودو بواسطة كود الصنف
            official_name = ""
            if ing_code:
                match = odoo_map_by_code.get(ing_code.lower())
                if match and match.get("name"):
                    official_name = match["name"]

            # في حال لم يتوفر في أودو نعتمد وصف الريسبي الأصلي
            final_name = official_name if official_name else (raw_desc or f"صنف {ing_code}")

            qty_g = c_num(row.get(col_qty_g)) if col_qty_g else 0.0
            qty_kg = c_num(row.get(col_qty_kg)) if col_qty_kg else 0.0
            cost_u = c_num(row.get(col_cost)) if col_cost else 0.0
            tot_c = c_num(row.get(col_tot)) if col_tot else 0.0

            if qty_kg > 0:
                quantity = qty_kg
                unit = "كيلو"
            elif qty_g > 0:
                quantity = qty_g
                unit = "غم"
            else:
                quantity = 1.0
                unit = "قطعة"

            if tot_c == 0.0 and cost_u > 0:
                tot_c = cost_u * (qty_kg if qty_kg > 0 else (qty_g / 1000.0 if qty_g > 0 else 1.0))

            subs = semi_dict.get(ing_code.lower(), [])
            is_sf = len(subs) > 0 or ing_code.startswith("SF")

            # مفتاح التجميع بالاسم والتاريخ لضمان فصل الأيام المختلفة
            group_key = f"{meal_name}____{date_str}"
            if group_key not in meals_dict:
                meals_dict[group_key] = {
                    "name": meal_name,
                    "date": date_str,
                    "display_title": f"{meal_name} ({date_str})" if date_str != "تاريخ غير محدد" else meal_name,
                    "code": f"STAFF-{len(meals_dict)+1:03d}",
                    "total_cost": 0.0,
                    "ingredients": []
                }

            meals_dict[group_key]["ingredients"].append({
                "code": ing_code,
                "name": final_name,
                "raw_description": raw_desc,
                "quantity": quantity,
                "unit": unit,
                "cost_per_unit": cost_u,
                "total_cost": tot_c,
                "is_semi_finished": is_sf,
                "sub_ingredients": subs
            })

    for m in meals_dict.values():
        if len(m["ingredients"]) > 0:
            m["total_cost"] = sum(i["total_cost"] for i in m["ingredients"])
            staff_meals.append(m)

    # ترتيب الوجبات زمنياً
    staff_meals.sort(key=lambda x: x["date"], reverse=True)

with open(os.path.join(out_dir, "staff_meals.json"), "w", encoding="utf-8") as f:
    json.dump(staff_meals, f, ensure_ascii=False, indent=2, allow_nan=False)
print(f"تم تصدير {len(staff_meals)} وجبة موظفين مفصلة بالتواريخ ومكوناتها الرسمية من أودو.")

# ==========================================
# 4. قراءة كافة شيتات طلبات مارت نهائي
# ==========================================
talabat_items = []
if p_talabat and os.path.exists(p_talabat):
    print(f"قراءة ملف طلبات مارت من: {p_talabat}...")
    xls_tal = pd.ExcelFile(p_talabat)
    for s_name in xls_tal.sheet_names:
        df_raw = pd.read_excel(xls_tal, sheet_name=s_name, header=None)
        if len(df_raw) < 2: continue

        header_row = 0
        found_hdr = False
        for r_idx in range(min(10, len(df_raw))):
            row_txt = " ".join([str(x) for x in df_raw.iloc[r_idx].values if pd.notna(x)]).lower()
            if any(k in row_txt for k in ["اسم", "name", "item", "sku", "باركود", "barcode", "سعر", "price"]):
                header_row = r_idx
                found_hdr = True
                break

        if found_hdr:
            df_tal = pd.read_excel(xls_tal, sheet_name=s_name, skiprows=header_row).dropna(how="all")
        else:
            df_tal = pd.read_excel(xls_tal, sheet_name=s_name).dropna(how="all")

        t_name_col = find_col(df_tal, ["اسم الصنف", "اسم المادة", "item name", "item description", "description", "اسم", "item", "name"])
        t_code_col = find_col(df_tal, ["sku", "item code", "رمز", "كود", "code", "reference"])
        t_barcode_col = find_col(df_tal, ["barcode", "باركود", "بار كود", "upc", "ean"])
        t_price_col = find_col(df_tal, ["سعر البيع", "retail price", "selling price", "سعر", "price", "بيع"])
        t_cost_col = find_col(df_tal, ["سعر الشراء", "cost price", "purchase price", "تكلفة", "cost", "شراء"])
        t_cat_col = find_col(df_tal, ["الفئة", "القسم", "category", "department", "subcategory", "قسم", "فئة"])

        for _, row in df_tal.iterrows():
            t_name = c_str(row.get(t_name_col)) if t_name_col else ""
            if not t_name or t_name.lower() in ["nan", "total", "المجموع"]: continue

            t_code = c_str(row.get(t_code_col)) if t_code_col else ""
            t_barcode = c_str(row.get(t_barcode_col)) if t_barcode_col else ""
            t_price = c_num(row.get(t_price_col)) if t_price_col else 0.0
            t_cost = c_num(row.get(t_cost_col)) if t_cost_col else 0.0

            matched_odoo = odoo_map_by_barcode.get(t_barcode.lower()) or odoo_map_by_code.get(t_code.lower())
            matched_odoo_code = matched_odoo.get("code", "") if matched_odoo else ""
            if matched_odoo and t_cost == 0.0:
                t_cost = matched_odoo.get("cost", 0.0)

            margin = ((t_price - t_cost) / t_price) if t_price > 0 else 0.0
            cat_val = c_str(row.get(t_cat_col)) if t_cat_col else s_name

            talabat_items.append({
                "name": t_name,
                "sku": t_code,
                "barcode": t_barcode,
                "category": cat_val if cat_val else "عام",
                "price": t_price,
                "cost": t_cost,
                "margin": margin,
                "odoo_code": matched_odoo_code
            })

with open(os.path.join(out_dir, "talabat_mart.json"), "w", encoding="utf-8") as f:
    json.dump(talabat_items, f, ensure_ascii=False, indent=2, allow_nan=False)
print(f"تم تصدير {len(talabat_items)} صنف من طلبات مارت بنجاح تام!")

print("🎉 اكتمل تحديث جميع قواعد البيانات بنجاح 100%!")
