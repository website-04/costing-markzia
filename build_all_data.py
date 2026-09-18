import os
import json
import math
import shutil
import datetime
import pandas as pd

p_costing = "Costing V21.xlsx"
if not os.path.exists(p_costing):
    p_costing = os.path.expanduser(r"~\Downloads\Costing V21.xlsx")

p_staff = r"C:\Users\NTC\Desktop\ريسبي وجبات الموظفين.xlsx"
if not os.path.exists(p_staff):
    p_staff = os.path.expanduser(r"~\Desktop\ريسبي وجبات الموظفين.xlsx")

p_odoo = os.path.expanduser(r"~\Downloads\اصناف اودو اخر تحديث (2).xlsx")
if not os.path.exists(p_odoo):
    p_odoo = r"C:\Users\NTC\Downloads\اصناف اودو اخر تحديث (2).xlsx"

p_talabat = r"C:\Users\NTC\Desktop\طلبات مارت نهائي (3).xlsx"
if not os.path.exists(p_talabat):
    p_talabat = os.path.expanduser(r"~\Desktop\طلبات مارت نهائي (3).xlsx")

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

def is_real_code(code_val):
    s = str(code_val).strip().upper()
    if not s or s in ["NAN", "NONE"]: return False
    if s.startswith("WH") or s.startswith("SF") or s.startswith("RM") or s.startswith("FP"):
        return True
    if "-" in s or "/" in s or len(s) < 4: return False
    return any(c.isdigit() for c in s) and any(c.isalpha() for c in s)

# ==========================================
# 1. دليل أودو الشامل
# ==========================================
odoo_items = []
odoo_map_by_code = {}
odoo_map_by_barcode = {}

if os.path.exists(p_odoo):
    print(f"قراءة دليل أودو...")
    df_odoo = pd.read_excel(p_odoo).dropna(how="all")
    for _, row in df_odoo.iterrows():
        vals = list(row.values)
        if len(vals) < 2: continue
        name = c_str(vals[0])
        code = c_str(vals[1]) if len(vals) > 1 else ""
        if not name: continue
        item_obj = {
            "code": code,
            "name": name,
            "category": c_str(vals[2]) if len(vals) > 2 else "عام",
            "cost": c_num(vals[3]) if len(vals) > 3 else 0.0,
            "price": c_num(vals[4]) if len(vals) > 4 else 0.0,
            "unit": c_str(vals[5]) if len(vals) > 5 else "قطعة",
            "barcode": c_str(vals[6]) if len(vals) > 6 else ""
        }
        odoo_items.append(item_obj)
        if code: odoo_map_by_code[code.lower()] = item_obj
        if item_obj["barcode"]: odoo_map_by_barcode[item_obj["barcode"].lower()] = item_obj

with open(os.path.join(out_dir, "odoo_catalog.json"), "w", encoding="utf-8") as f:
    json.dump(odoo_items, f, ensure_ascii=False, indent=2, allow_nan=False)

# ==========================================
# 2. شجرة التكاليف والـ BOM
# ==========================================
semi_dict = {}
finished_items = {}

if os.path.exists(p_costing):
    print(f"قراءة ملف التكاليف...")
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

# ==========================================
# 3. استخراج ريسبي ومكونات وجبات الموظفين الحقيقية
# ==========================================
staff_meals = []
if os.path.exists(p_staff):
    print(f"قراءة ريسبي وجبات الموظفين بدقة المكونات...")
    xls_staff = pd.ExcelFile(p_staff)
    meals_dict = {}

    for s_name in xls_staff.sheet_names:
        df_raw = pd.read_excel(xls_staff, sheet_name=s_name, header=None)
        if len(df_raw) < 2: continue

        # البحث عن رأس الجدول
        hdr_idx = 0
        for r in range(min(12, len(df_raw))):
            row_s = " ".join([str(x) for x in df_raw.iloc[r].values if pd.notna(x)]).lower()
            if "كود الصنف" in row_s or "رسبي الوجبة" in row_s or "كمية رسبي" in row_s:
                hdr_idx = r
                break

        df_s = pd.read_excel(xls_staff, sheet_name=s_name, skiprows=hdr_idx).dropna(how="all")

        # تعبئة الخلايا المدمجة للتواريخ وأسماء الوجبات
        for c in df_s.columns[:3]:
            df_s[c] = df_s[c].ffill()

        for _, row in df_s.iterrows():
            vals = list(row.values)
            if len(vals) < 4: continue

            # البحث عن كود المادة الحقيقي (WH أو SF)
            ing_code = ""
            for v in vals:
                if is_real_code(v):
                    ing_code = c_str(v)
                    break

            # إذا لم يوجد كود مادة حقيقي، يتم تجاهل الصف تماماً (لحذف صفوف الملخص والمجاميع)
            if not ing_code: continue

            # اسم الوجبة والتاريخ
            meal_name = ""
            raw_desc = ""
            date_str = ""

            # فحص الأعمدة المحددة
            for idx, v in enumerate(vals):
                vs = c_str(v)
                if not vs: continue
                # فحص التاريخ
                if not date_str and any(ch.isdigit() for ch in vs) and ("-" in vs or "/" in vs):
                    try:
                        date_str = pd.to_datetime(vs, dayfirst=True).strftime("%Y-%m-%d")
                    except:
                        date_str = vs.split(" ")[0]
                # فحص اسم الوجبة
                elif not meal_name and any(w in vs for w in ["اوزي", "منسف", "قدرة", "ملوخية", "فاصوليا", "بازيلا", "داوود", "برياني", "كبسة", "دجاج", "لحم", "شعرية", "شاكرية", "فاهيتا", "بامية", "منزلة", "مجدرة", "مندي", "شاورما"]):
                    meal_name = vs
                # فحص وصف المادة
                elif not raw_desc and vs != ing_code and vs != meal_name and not vs.replace(".","").isdigit():
                    raw_desc = vs

            if not meal_name:
                meal_name = c_str(vals[2]) if len(vals) > 2 else "وجبة موظفين"

            if not date_str:
                date_str = "2026-08-26"

            # الاسم الرسمي للمادة من أودو عبر الكود
            match_odoo = odoo_map_by_code.get(ing_code.lower())
            official_name = match_odoo["name"] if match_odoo else (raw_desc or f"مادة {ing_code}")

            # استخراج الكميات والتكاليف
            qty_g = 0.0
            qty_kg = 0.0
            cost_u = 0.0
            tot_c = 0.0

            numeric_vals = [c_num(x) for x in vals if str(x).replace(".","").replace("-","").isdigit() and c_num(x) > 0]
            if len(numeric_vals) >= 4:
                qty_g = numeric_vals[0]
                qty_kg = numeric_vals[1]
                cost_u = numeric_vals[2]
                tot_c = numeric_vals[3]
            elif len(numeric_vals) == 3:
                qty_kg = numeric_vals[0]
                cost_u = numeric_vals[1]
                tot_c = numeric_vals[2]

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
                tot_c = cost_u * (qty_kg if qty_kg > 0 else (qty_g / 1000.0 if qty_g > 0 else quantity))

            subs = semi_dict.get(ing_code.lower(), [])
            is_sf = len(subs) > 0 or ing_code.startswith("SF")

            group_key = f"{meal_name}____{date_str}"
            if group_key not in meals_dict:
                meals_dict[group_key] = {
                    "name": meal_name,
                    "date": date_str,
                    "code": f"STAFF-{len(meals_dict)+1:03d}",
                    "total_cost": 0.0,
                    "ingredients": []
                }

            meals_dict[group_key]["ingredients"].append({
                "code": ing_code,
                "name": official_name,
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

    staff_meals.sort(key=lambda x: x["date"], reverse=True)

with open(os.path.join(out_dir, "staff_meals.json"), "w", encoding="utf-8") as f:
    json.dump(staff_meals, f, ensure_ascii=False, indent=2, allow_nan=False)
print(f"تم تصدير {len(staff_meals)} وجبة موظفين حقيقية بجميع مكوناتها التفصيلية من أودو.")

# ==========================================
# 4. طلبات مارت
# ==========================================
talabat_items = []
if os.path.exists(p_talabat):
    print(f"قراءة طلبات مارت...")
    xls_tal = pd.ExcelFile(p_talabat)
    for s_name in xls_tal.sheet_names:
        df_tal = pd.read_excel(xls_tal, sheet_name=s_name).dropna(how="all")
        for _, row in df_tal.iterrows():
            vals = list(row.values)
            if len(vals) < 3: continue
            name = c_str(vals[0])
            if not name or name.lower() in ["nan", "total", "المجموع"]: continue
            sku = c_str(vals[1]) if len(vals) > 1 else ""
            barcode = c_str(vals[2]) if len(vals) > 2 else ""
            price = c_num(vals[3]) if len(vals) > 3 else 0.0
            cost = c_num(vals[4]) if len(vals) > 4 else 0.0

            matched_odoo = odoo_map_by_barcode.get(barcode.lower()) or odoo_map_by_code.get(sku.lower())
            matched_odoo_code = matched_odoo.get("code", "") if matched_odoo else ""
            if matched_odoo and cost == 0.0: cost = matched_odoo.get("cost", 0.0)
            margin = ((price - cost) / price) if price > 0 else 0.0

            talabat_items.append({
                "name": name, "sku": sku, "barcode": barcode, "category": s_name,
                "price": price, "cost": cost, "margin": margin, "odoo_code": matched_odoo_code
            })

with open(os.path.join(out_dir, "talabat_mart.json"), "w", encoding="utf-8") as f:
    json.dump(talabat_items, f, ensure_ascii=False, indent=2, allow_nan=False)

print("🎉 اكتمل استخراج البيانات بنجاح 100%!")
