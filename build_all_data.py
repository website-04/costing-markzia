import os
import json
import math
import re
import pandas as pd

p_odoo_master = r"C:\Users\NTC\Desktop\اودوو شامل اصناف وريسبي.xlsx"
if not os.path.exists(p_odoo_master): p_odoo_master = os.path.expanduser(r"~\Desktop\اودوو شامل اصناف وريسبي.xlsx")

p_costing = "Costing V21.xlsx"
if not os.path.exists(p_costing): p_costing = os.path.expanduser(r"~\Downloads\Costing V21.xlsx")

p_staff = r"C:\Users\NTC\Desktop\ريسبي وجبات الموظفين.xlsx"
if not os.path.exists(p_staff): p_staff = os.path.expanduser(r"~\Desktop\ريسبي وجبات الموظفين.xlsx")

p_talabat = r"C:\Users\NTC\Desktop\طلبات مارت نهائي (3).xlsx"
if not os.path.exists(p_talabat): p_talabat = os.path.expanduser(r"~\Desktop\طلبات مارت نهائي (3).xlsx")

out_dir = os.path.join("assets", "data")
os.makedirs(out_dir, exist_ok=True)

def c_str(v):
    if pd.isna(v) or v is None: return ""
    s = str(v).replace("*****", "").strip()
    return "" if s.lower() in ["nan", "none"] else s

def c_num(v):
    try:
        if pd.isna(v) or v is None: return 0.0
        f = float(v)
        return 0.0 if (math.isnan(f) or math.isinf(f)) else round(f, 3)
    except:
        return 0.0

def find_col(df, inc_keys, exc_keys=[]):
    for col in df.columns:
        c = str(col).lower().replace("\n", " ").strip()
        if any(k in c for k in inc_keys):
            if not any(e in c for e in exc_keys):
                return col
    return None

# ====================================================
# 1. دليل أودو الشامل
# ====================================================
odoo_items = []
odoo_map_by_code = {}

if os.path.exists(p_odoo_master):
    xls_m = pd.ExcelFile(p_odoo_master)

    s_kamel = next((s for s in xls_m.sheet_names if "كامل" in s), None)
    if s_kamel:
        df_k = pd.read_excel(xls_m, sheet_name=s_kamel).dropna(how="all")
        col_code = find_col(df_k, ["معرف", "كود", "code", "مرجع"]) or df_k.columns[0]
        col_name = find_col(df_k, ["اسم", "name", "صنف"]) or df_k.columns[1]
        col_cost = find_col(df_k, ["تكلفة", "كلفة", "cost"])
        col_unit = find_col(df_k, ["وحدة", "unit"])
        col_qty = find_col(df_k, ["كمية", "qty"])

        for _, r in df_k.iterrows():
            code = c_str(r.get(col_code))
            name = c_str(r.get(col_name))
            if not name or name.replace(".","").isdigit(): continue
            cost = c_num(r.get(col_cost)) if col_cost else 0.0
            qty = c_num(r.get(col_qty)) if col_qty and c_num(r.get(col_qty)) > 0 else 1.0
            unit = c_str(r.get(col_unit)) if col_unit else "كغ"

            item_obj = {
                "code": code, "name": name, "category": "كامل",
                "quantity": qty, "cost_per_unit": cost,
                "total_cost": round(qty * cost, 3), "price": 0.0, "unit": unit, "barcode": ""
            }
            odoo_items.append(item_obj)
            if code: odoo_map_by_code[code.lower()] = item_obj

    s_mowared = next((s for s in xls_m.sheet_names if "مورد" in s), None)
    if s_mowared:
        df_sup = pd.read_excel(xls_m, sheet_name=s_mowared).dropna(how="all")
        col_code = find_col(df_sup, ["معرف", "كود", "code"]) or df_sup.columns[0]
        col_name = find_col(df_sup, ["اسم", "name", "طبخة"]) or df_sup.columns[1]
        col_sec = find_col(df_sup, ["قسم", "فئة", "section"])
        col_prc = find_col(df_sup, ["سعر", "price"])

        for _, r in df_sup.iterrows():
            code = c_str(r.get(col_code))
            name = c_str(r.get(col_name))
            if not name: continue
            price = c_num(r.get(col_prc)) if col_prc else 0.0
            sec = c_str(r.get(col_sec)) if col_sec else "منتجات المورد"

            if code and code.lower() in odoo_map_by_code:
                odoo_map_by_code[code.lower()]["price"] = price
                odoo_map_by_code[code.lower()]["category"] = sec
            else:
                item_obj = {
                    "code": code, "name": name, "category": sec,
                    "quantity": 1.0, "cost_per_unit": 0.0,
                    "total_cost": 0.0, "price": price, "unit": "وجبة", "barcode": ""
                }
                odoo_items.append(item_obj)
                if code: odoo_map_by_code[code.lower()] = item_obj

    s_ameel = next((s for s in xls_m.sheet_names if "عميل" in s or "زبون" in s), None)
    if s_ameel:
        df_cust = pd.read_excel(xls_m, sheet_name=s_ameel).dropna(how="all")
        col_code = find_col(df_cust, ["معرف", "كود"]) or df_cust.columns[0]
        col_name = find_col(df_cust, ["اسم", "منتج"]) or df_cust.columns[1]
        col_sec = find_col(df_cust, ["تصنيف", "قسم"])

        for _, r in df_cust.iterrows():
            code = c_str(r.get(col_code))
            name = c_str(r.get(col_name))
            if not name: continue
            sec = c_str(r.get(col_sec)) if col_sec else "منتجات العميل"
            if code and code.lower() in odoo_map_by_code:
                odoo_map_by_code[code.lower()]["category"] = sec
            else:
                item_obj = {
                    "code": code, "name": name, "category": sec,
                    "quantity": 1.0, "cost_per_unit": 0.0,
                    "total_cost": 0.0, "price": 0.0, "unit": "حبة", "barcode": ""
                }
                odoo_items.append(item_obj)
                if code: odoo_map_by_code[code.lower()] = item_obj

with open(os.path.join(out_dir, "odoo_catalog.json"), "w", encoding="utf-8") as f:
    json.dump(odoo_items, f, ensure_ascii=False, indent=2, allow_nan=False)

# ====================================================
# 2. شجرة التكاليف Costing V21
# ====================================================
semi_dict = {}
standard_bom_map = {}
recipes_list = []

if os.path.exists(p_costing):
    xls_c = pd.ExcelFile(p_costing)
    if "Semi Finished Recipe" in xls_c.sheet_names:
        df_semi = pd.read_excel(xls_c, sheet_name="Semi Finished Recipe")
        curr_sf_code, curr_sf_name = "", ""

        for _, row in df_semi.iterrows():
            parent_code = c_str(row.get('odoo')) or c_str(row.get('SF Item\nCode'))
            parent_name = c_str(row.get('SF Item\nName'))
            if parent_name:
                curr_sf_name = parent_name
                curr_sf_code = parent_code

            ing_code = c_str(row.get('odoo.1')) or c_str(row.get('RM Item\nNew Code'))
            ing_name = c_str(row.get('Complete Item Description'))
            if not ing_name and not ing_code: continue

            sub_item = {
                "rm_code": ing_code,
                "name": ing_name or "مادة خام",
                "standard_quantity": c_num(row.get('الكمية المعادلة') or row.get('Quantity') or 1.0),
                "unit": c_str(row.get('Unit')) or "غم",
                "cost_per_unit": c_num(row.get('Cost Per Unit') or row.get('Cost per Unit')),
                "total_cost": c_num(row.get('Total Cost'))
            }

            for k in [curr_sf_code, parent_code]:
                if k and len(k) >= 3:
                    k_l = k.lower()
                    if k_l not in semi_dict: semi_dict[k_l] = []
                    semi_dict[k_l].append(sub_item)
                    standard_bom_map[k_l] = {
                        "name": curr_sf_name, "code": k,
                        "standard_quantity": sub_item["standard_quantity"],
                        "unit": sub_item["unit"], "cost": sub_item["total_cost"]
                    }

    if "Finished Recipe" in xls_c.sheet_names:
        df_fin = pd.read_excel(xls_c, sheet_name="Finished Recipe")
        dishes_map = {}

        for _, row in df_fin.iterrows():
            parent_code = c_str(row.get('odoo')) or c_str(row.get('Menu Item\nNew Code'))
            parent_name = c_str(row.get('Menu Item\nName'))
            if not parent_code and not parent_name: continue

            key = (parent_code or parent_name).lower()
            if key not in dishes_map:
                dish_cost = c_num(row.get('تكلفة الصنف') or row.get('Total Cost'))
                dishes_map[key] = {
                    "code": parent_code or key,
                    "odoo_code": parent_code,
                    "recipe_code": c_str(row.get('Menu Item\nNew Code')),
                    "name": parent_name,
                    "category": c_str(row.get('Category') or row.get('Section') or "طعام"),
                    "selling_price": 0.0,
                    "total_cost": dish_cost,
                    "food_cost_percentage": 0.0,
                    "ingredients": []
                }

            ing_code = c_str(row.get('odoo.1')) or c_str(row.get('RM Item\nNew Code'))
            ing_name = c_str(row.get('Complete Item Description'))
            if not ing_code and not ing_name: continue

            ing_qty = c_num(row.get('Quantity') or 1.0)
            ing_unit = c_str(row.get('Unit')) or "غم"
            ing_cost_u = c_num(row.get('Cost per Unit') or row.get('Cost Per Unit'))
            ing_tot_c = c_num(row.get('Total Cost'))

            match_od = odoo_map_by_code.get(ing_code.lower())
            official_name = match_od["name"] if match_od else (ing_name or f"مادة {ing_code}")
            subs = semi_dict.get(ing_code.lower(), [])

            dishes_map[key]["ingredients"].append({
                "code": ing_code,
                "name": official_name,
                "raw_description": ing_name,
                "standard_quantity": f"{ing_qty} {ing_unit}",
                "actual_quantity": ing_qty,
                "unit": ing_unit,
                "cost_per_unit": ing_cost_u,
                "total_cost": ing_tot_c,
                "is_semi_finished": len(subs) > 0 or ing_code.startswith("SF"),
                "sub_ingredients": subs
            })

        for d in dishes_map.values():
            if d["total_cost"] == 0.0 and len(d["ingredients"]) > 0:
                d["total_cost"] = round(sum(i["total_cost"] for i in d["ingredients"]), 3)
            recipes_list.append(d)

with open(os.path.join(out_dir, "costing_data.json"), "w", encoding="utf-8") as f:
    json.dump(recipes_list, f, ensure_ascii=False, indent=2, allow_nan=False)

# ====================================================
# 3. وجبات الموظفين - استخراج اسم الأكلة الحقيقي (مثل مجدرة)
# ====================================================
staff_meals = []

if os.path.exists(p_staff):
    xls_s = pd.ExcelFile(p_staff)
    meals_dict = {}

    for s_name in xls_s.sheet_names:
        df_s = pd.read_excel(xls_s, sheet_name=s_name)
        if len(df_s) < 2: continue

        # الكشف التلقائي عن عامود اسم الطبخة (مثل: مجدرة، داوود باشا)
        # عامود الوصفات يحتوي على أوزان (10كيلو، 7كيلو) بينما عامود اسم الأكلة نقي تماماً
        col_actual_dish = None
        col_recipe_desc = None
        col_code = find_col(df_s, ["معرف", "كود", "code", "odoo"]) or df_s.columns[1]
        col_date = find_col(df_s, ["تاريخ", "date"])
        col_qty_kg = find_col(df_s, ["كيلو", "كغ", "وزن", "kg"])
        col_qty_g = find_col(df_s, ["غرام", "جرام", "g"])
        col_cost = find_col(df_s, ["كلفة", "تكلفة", "سعر", "cost"])
        col_tot = find_col(df_s, ["اجمالي", "إجمالي", "total"])

        # فحص الأعمدة لاكتشاف أين يقع اسم الأكلة النقي (مجدرة، فاصوليا، داوود باشا)
        for col in df_s.columns:
            sample_vals = [str(x).strip() for x in df_s[col].dropna().head(30).tolist()]
            has_mojadara = any("مجدرة" in v for v in sample_vals)
            has_dishes = any(any(k in v for k in ["مجدرة", "داوود", "فاصوليا", "بازيلا", "معكرونة", "كبسة", "منسف", "ملوخية", "بامية", "شاورما", "كفتة", "برغر", "مقلوبة"]) for v in sample_vals)
            has_weights = any(any(k in v for k in ["كيلو", "كغ", "غرام", "جرام", "كيس"]) for v in sample_vals)

            if has_mojadara or (has_dishes and not has_weights):
                col_actual_dish = col
            elif has_weights and has_dishes:
                col_recipe_desc = col

        if not col_actual_dish:
            # إذا لم يكن هناك عامود منفصل، نبحث في الأعمدة عن اسم الطبخة
            for col in df_s.columns:
                if col != col_code and col != col_qty_kg and col != col_tot:
                    col_actual_dish = col
                    break

        curr_tracked_dish = ""
        clean_sheet_date = s_name.replace("(", "").replace(")", "").strip()
        curr_tracked_date = clean_sheet_date

        for _, row in df_s.iterrows():
            ing_code = c_str(row.get(col_code))
            dish_val = c_str(row.get(col_actual_dish)) if col_actual_dish else ""
            desc_val = c_str(row.get(col_recipe_desc)) if col_recipe_desc else ""
            date_val = c_str(row.get(col_date)) if col_date else ""

            if date_val and any(c.isdigit() for c in date_val):
                curr_tracked_date = date_val.split()[0].replace("-", "/")

            # تنظيف واستخراج اسم الطبخة الحقيقي حصراً
            # استبعاد الأوزان مثل (10كيلو أو 7كيلو) لتظهر اسم الطبخة مثل: مجدرة أو داوود باشا
            candidate_dish = dish_val or desc_val
            if candidate_dish:
                # حذف أي أوزان ملحقة بالاسم
                cleaned_dish = re.sub(r'\s*\d+\s*(?:كيلو|كغ|غرام|جرام|كيس).*', '', candidate_dish).strip()
                # إزالة كلمة ارز بشعرية إذا كانت متبوعة باسم الطبيخ
                m_sub = re.search(r'(?:ارز بشعرية|أرز بشعرية|ارز|أرز)\s+(.+)', cleaned_dish)
                if m_sub and len(m_sub.group(1).strip()) >= 3:
                    cleaned_dish = m_sub.group(1).strip()

                if len(cleaned_dish) >= 3 and not any(w in cleaned_dish for w in ["كيلو", "غرام"]):
                    curr_tracked_dish = cleaned_dish

            if not ing_code or ing_code.lower() in ["nan", "none", "المجموع", "total"]:
                continue
            if re.match(r'^\d{1,2}[-/]\d{1,2}', ing_code):
                curr_tracked_date = ing_code.replace("-", "/")
                continue

            active_dish_name = curr_tracked_dish if curr_tracked_dish else "وجبة موظفين"
            active_dish_name = active_dish_name.replace("(", "").replace(")", "").strip()

            match_od = odoo_map_by_code.get(ing_code.lower())
            official_name = match_od["name"] if match_od else (desc_val or f"مادة {ing_code}")

            qty_kg = c_num(row.get(col_qty_kg)) if col_qty_kg else 0.0
            qty_g = c_num(row.get(col_qty_g)) if col_qty_g else 0.0
            cost_u = c_num(row.get(col_cost)) if col_cost else 0.0
            tot_c = c_num(row.get(col_tot)) if col_tot else 0.0

            actual_qty = qty_kg if qty_kg > 0 else (round(qty_g / 1000.0, 3) if qty_g >= 100 else qty_g)
            if actual_qty == 0.0: actual_qty = 1.0

            if tot_c == 0.0 and cost_u > 0:
                tot_c = round(actual_qty * cost_u, 3)
            elif tot_c > 0 and cost_u == 0.0 and actual_qty > 0:
                cost_u = round(tot_c / actual_qty, 3)

            std_info = standard_bom_map.get(ing_code.lower())
            std_qty = f"{std_info['standard_quantity']} {std_info['unit']}" if std_info else "معياري 1 كغ"
            subs = semi_dict.get(ing_code.lower(), [])

            group_key = f"{active_dish_name}____{curr_tracked_date}"
            if group_key not in meals_dict:
                meals_dict[group_key] = {
                    "name": active_dish_name,
                    "date": curr_tracked_date,
                    "code": f"STAFF-{len(meals_dict)+1:03d}",
                    "total_cost": 0.0,
                    "ingredients": []
                }

            meals_dict[group_key]["ingredients"].append({
                "code": ing_code,
                "name": official_name,
                "raw_description": desc_val,
                "actual_quantity": actual_qty,
                "unit": "كيلو",
                "standard_quantity": std_qty,
                "cost_per_unit": cost_u,
                "total_cost": tot_c,
                "is_semi_finished": len(subs) > 0 or ing_code.startswith("SF"),
                "sub_ingredients": subs
            })

    for m in meals_dict.values():
        if len(m["ingredients"]) > 0:
            m["total_cost"] = round(sum(i["total_cost"] for i in m["ingredients"]), 3)
            staff_meals.append(m)

    staff_meals.sort(key=lambda x: str(x["date"]), reverse=True)

with open(os.path.join(out_dir, "staff_meals.json"), "w", encoding="utf-8") as f:
    json.dump(staff_meals, f, ensure_ascii=False, indent=2, allow_nan=False)

# ====================================================
# 4. طلبات مارت
# ====================================================
talabat_sheets_data = []

cuts_dict = {
    "كتف + فخد + رقاب + قطع الشيف": ["كتف", "فخد", "رقاب", "قطع الشيف", "شيف"],
    "شقف": ["شقف"],
    "لية": ["لية", "ليه"],
    "ريش": ["ريش"],
    "رفالات + قص مجروم + زوايد": ["رفالات", "قص مجروم", "زوايد", "مجروم"],
    "بدنيات": ["بدنيات"],
    "نتر": ["نتر"],
    "كلاوي": ["كلاوي"],
    "خصاوي": ["خصاوي"],
    "فتايل": ["فتايل", "فتائل", "فتيل"],
    "عروق + عرقيب + عظم": ["عروق", "عرقيب", "عظم"],
    "اضلاع خروف 500غرام": ["اضلاع", "أضلاع"],
}

if os.path.exists(p_talabat):
    xls_t = pd.ExcelFile(p_talabat)

    for s_name in xls_t.sheet_names:
        df_t = pd.read_excel(xls_t, sheet_name=s_name, header=None)
        if len(df_t) < 2: continue

        n_rows, n_cols = df_t.shape
        all_text = " ".join([str(x) for x in df_t.values.flatten() if pd.notna(x)])

        m_date = re.search(r'(\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?)', s_name)
        m_batch = re.search(r'\((\d+)\)', s_name)
        clean_date = m_date.group(1).replace('-', '/') if m_date else s_name.replace('(', '').replace(')', '').strip()
        batch_num = m_batch.group(1) if m_batch else ""

        if batch_num:
            display_title = f"{clean_date} - دفعة {batch_num}"
            sub_title = f"دفعة {batch_num} • حسبة الخروف"
        else:
            display_title = f"{clean_date}"
            sub_title = "حسبة تفصيل وتقطيع الخروف"

        is_lamb = any(k in all_text for k in ["خروف", "خرفان", "كتف", "شقف", "ريش", "بدنيات", "فتايل", "عروق"]) or "خروف" in s_name

        if is_lamb:
            sheep_count, price_per_kg, invoice_total = 0.0, 0.0, 0.0
            weight_received, weight_cut, waste_loss = 0.0, 0.0, 0.0

            for r in range(min(6, n_rows)):
                for c in range(n_cols):
                    txt = str(df_t.iat[r, c]).strip()
                    if "عدد الخرفان" in txt and r + 1 < n_rows:
                        v = c_num(df_t.iat[r + 1, c])
                        if v > 0: sheep_count = v
                    if any(k in txt for k in ["سعر كيلو", "الفاتورة"]) and r + 1 < n_rows:
                        v = c_num(df_t.iat[r + 1, c])
                        if v > 0: price_per_kg = v
                    if any(k in txt for k in ["اجمالي السعر", "إجمالي السعر"]) and r + 1 < n_rows:
                        v = c_num(df_t.iat[r + 1, c])
                        if v > 0: invoice_total = v

            c_name_col = -1
            r_head = -1
            for r in range(min(10, n_rows)):
                for c in range(n_cols):
                    if "اسم الصنف" in str(df_t.iat[r, c]):
                        c_name_col = c
                        r_head = r
                        break
                if c_name_col != -1: break

            if c_name_col == -1: c_name_col = 3
            c_qty_col = -1
            for c in range(c_name_col + 1, n_cols):
                for r in range(min(10, n_rows)):
                    if "الكمية" in str(df_t.iat[r, c]):
                        c_qty_col = c
                        break
                if c_qty_col != -1: break

            if c_qty_col == -1: c_qty_col = 6
            c_pct_col = c_qty_col + 1 if c_qty_col + 1 < n_cols else 7
            c_price_col = max(0, c_name_col - 2)
            c_total_col = max(0, c_name_col - 1)

            cuts_list = []
            for r in range(r_head + 1 if r_head != -1 else 3, n_rows):
                row_str = " ".join([str(df_t.iat[r, c]) for c in range(n_cols) if pd.notna(df_t.iat[r, c])])
                name_val = str(df_t.iat[r, c_name_col]).strip()

                if "الوزن عند استلام" in row_str or "استلام ( الفاتورة )" in row_str:
                    weight_received = c_num(df_t.iat[r, c_qty_col])
                    continue
                if "الوزن قبل التقطيع" in row_str or "قبل التقطيع" in row_str:
                    weight_cut = c_num(df_t.iat[r, c_qty_col])
                    continue
                if "الفاقد" in row_str:
                    waste_loss = c_num(df_t.iat[r, c_qty_col])
                    continue
                if "صافي الوزن" in row_str:
                    net_w = c_num(df_t.iat[r, c_qty_col])
                    if net_w > 0: weight_cut = net_w
                    continue

                matched_cut = None
                for std_name, kws in cuts_dict.items():
                    if any(k in name_val for k in kws) or any(k in row_str for k in kws):
                        matched_cut = std_name
                        break

                if matched_cut:
                    p_val = c_num(df_t.iat[r, c_price_col])
                    tot_val = c_num(df_t.iat[r, c_total_col])
                    q_val = c_num(df_t.iat[r, c_qty_col])
                    pct_raw = str(df_t.iat[r, c_pct_col]).strip() if c_pct_col < n_cols else ""

                    pct_str = ""
                    if "%" in pct_raw: pct_str = pct_raw
                    else:
                        p_f = c_num(pct_raw)
                        if 0 < p_f <= 1.0: pct_str = f"{round(p_f * 100)}%"
                        elif p_f > 1.0: pct_str = f"{round(p_f)}%"

                    if tot_val == 0.0 and q_val > 0 and p_val > 0:
                        tot_val = round(q_val * p_val, 3)
                    elif p_val == 0.0 and tot_val > 0 and q_val > 0:
                        p_val = round(tot_val / q_val, 3)

                    if any(k in matched_cut for k in ["بدنيات", "نتر"]): status = "highlight_red"
                    elif any(k in matched_cut for k in ["ريش", "رفالات", "كلاوي", "خصاوي"]): status = "highlight_yellow"
                    elif any(k in matched_cut for k in ["كتف", "فخد", "شيف"]): status = "primary"
                    else: status = "normal"

                    cuts_list.append({
                        "name": matched_cut,
                        "qty": round(q_val, 2),
                        "percentage": pct_str,
                        "price": round(p_val, 3),
                        "total": round(tot_val, 3),
                        "status": status
                    })

            total_cuts_weight = round(sum(c["qty"] for c in cuts_list), 2)
            total_cuts_val = round(sum(c["total"] for c in cuts_list), 3)

            if invoice_total == 0.0: invoice_total = total_cuts_val
            if weight_cut == 0.0: weight_cut = total_cuts_weight
            if weight_received == 0.0: weight_received = round(weight_cut + waste_loss, 2)
            if waste_loss == 0.0 and weight_received > weight_cut:
                waste_loss = round(weight_received - weight_cut, 2)
            if price_per_kg == 0.0 and weight_received > 0 and invoice_total > 0:
                price_per_kg = round(invoice_total / weight_received, 3)

            for c in cuts_list:
                if not c["percentage"] or c["percentage"] in ["0%", ""]:
                    if total_cuts_weight > 0 and c["qty"] > 0:
                        c["percentage"] = f"{round((c['qty'] / total_cuts_weight) * 100)}%"
                    else:
                        c["percentage"] = "0%"

            talabat_sheets_data.append({
                "type": "lamb_report",
                "sheet_name": s_name,
                "display_title": display_title,
                "sub_title": sub_title,
                "date": clean_date,
                "sheep_count": sheep_count,
                "price_per_kg": price_per_kg,
                "invoice_total": invoice_total,
                "weight_received": weight_received,
                "weight_cut": weight_cut,
                "waste_loss": waste_loss,
                "cuts_total_value": total_cuts_val,
                "cuts": cuts_list
            })
        else:
            items_list = []
            for _, r in df_t.iterrows():
                vals = list(r.values)
                if len(vals) < 3: continue
                n = c_str(vals[0])
                if not n or n.replace(".","").isdigit() or n in ["nan", "total", "المجموع"]: continue
                pr = c_num(vals[3]) if len(vals) > 3 else 0.0
                co = c_num(vals[4]) if len(vals) > 4 else 0.0
                qty = c_num(vals[2]) if len(vals) > 2 and c_num(vals[2]) > 0 else 1.0
                items_list.append({
                    "name": n, "sku": c_str(vals[1]),
                    "quantity": qty, "price": pr, "cost": co,
                    "total": round(qty * pr, 3) if pr > 0 else 0.0
                })

            if len(items_list) > 0:
                talabat_sheets_data.append({
                    "type": "daily_sheet",
                    "sheet_name": s_name,
                    "display_title": f"{clean_date} - كشف طلبات",
                    "sub_title": f"كشف مبيعات • {clean_date}",
                    "date": clean_date,
                    "batch_label": f"دفعة {batch_num}" if batch_num else "",
                    "items_count": len(items_list),
                    "total_sales": round(sum(it["total"] for it in items_list), 3),
                    "items": items_list
                })

with open(os.path.join(out_dir, "talabat_mart.json"), "w", encoding="utf-8") as f:
    json.dump(talabat_sheets_data, f, ensure_ascii=False, indent=2, allow_nan=False)

print("🎉 اكتمل بنجاح استخراج أسماء الطبخات الحقيقية (مثل مجدرة) وتجميع الوصفات!")
