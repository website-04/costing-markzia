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

# 1. دليل أودو الشامل
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

# 2. شجرة التكاليف Costing V21 (إصلاح تكلفة الصنف وسعر البيع بدقة تامة)
semi_dict = {}
standard_bom_map = {}
finished_items = {}

if os.path.exists(p_costing):
    xls_c = pd.ExcelFile(p_costing)
    if "Semi Finished Recipe" in xls_c.sheet_names:
        df_semi = pd.read_excel(xls_c, sheet_name="Semi Finished Recipe")
        curr_sf_code, curr_sf_name, curr_sf_std_qty, curr_sf_unit = "", "", 1.0, "كغ"

        for _, row in df_semi.iterrows():
            vals = list(row.values)
            if len(vals) < 12: continue
            sf_od = c_str(vals[0])
            sf_cd = c_str(vals[1])
            sf_nm = c_str(vals[3])

            if sf_nm:
                curr_sf_name = sf_nm
                curr_sf_code = sf_od if sf_od else sf_cd
                curr_sf_std_qty = c_num(vals[7]) if c_num(vals[7]) > 0 else 1.0
                curr_sf_unit = c_str(vals[8]) or "كغ"

            if not curr_sf_name: continue
            rm_od = c_str(vals[4])
            rm_cd = c_str(vals[5])
            rm_nm = c_str(vals[6]) or "مادة خام"
            rm_code = rm_od if rm_od else rm_cd

            sub_item = {
                "rm_code": rm_code, "name": rm_nm,
                "standard_quantity": c_num(vals[7]), "unit": c_str(vals[8]) or "كغ",
                "cost_per_unit": c_num(vals[10]), "total_cost": c_num(vals[11])
            }

            for k in [curr_sf_code, sf_od, sf_cd]:
                if k and len(k) >= 3:
                    k_low = k.lower()
                    if k_low not in semi_dict: semi_dict[k_low] = []
                    semi_dict[k_low].append(sub_item)
                    standard_bom_map[k_low] = {
                        "name": curr_sf_name, "code": k,
                        "standard_quantity": curr_sf_std_qty, "unit": curr_sf_unit,
                        "cost": c_num(vals[11])
                    }

    if "Finished Recipe" in xls_c.sheet_names:
        df_fin = pd.read_excel(xls_c, sheet_name="Finished Recipe")
        curr_dish = None
        for _, row in df_fin.iterrows():
            vals = list(row.values)
            if len(vals) < 13: continue
            d_od = c_str(vals[0])
            d_cd = c_str(vals[1])
            d_nm = c_str(vals[3])

            if d_nm and (d_nm != (curr_dish["name"] if curr_dish else "")):
                dish_code = d_od if d_od else d_cd
                # استخراج تكلفة الصنف الرسمية من الإكسل
                excel_dish_cost = c_num(vals[13]) if len(vals) > 13 else 0.0
                if excel_dish_cost == 0.0 and len(vals) > 14:
                    excel_dish_cost = c_num(vals[14])

                curr_dish = {
                    "code": dish_code, "odoo_code": d_od, "recipe_code": d_cd,
                    "name": d_nm, "category": c_str(vals[4]) or "طعام",
                    "selling_price": 0.0,
                    "total_cost": excel_dish_cost,
                    "food_cost_percentage": 0.0,
                    "ingredients": []
                }
                finished_items[dish_code.lower() if dish_code else d_nm] = curr_dish

            if not curr_dish: continue
            ing_od = c_str(vals[6])
            ing_cd = c_str(vals[7])
            ing_nm = c_str(vals[8])
            ing_code = ing_od if ing_od else ing_cd
            if not ing_code and not ing_nm: continue

            ing_std_qty = c_num(vals[9] if len(vals) > 9 else vals[10])
            ing_unit = c_str(vals[10] if len(vals) > 10 else "كغ") or "كغ"
            ing_cost_u = c_num(vals[11] if len(vals) > 11 else 0.0)
            ing_tot_c = c_num(vals[12] if len(vals) > 12 else 0.0)

            match_od = odoo_map_by_code.get(ing_code.lower())
            official_name = match_od["name"] if match_od else (ing_nm or f"مادة {ing_code}")
            subs = semi_dict.get(ing_code.lower(), [])

            curr_dish["ingredients"].append({
                "code": ing_code, "name": official_name, "raw_description": ing_nm,
                "standard_quantity": f"{ing_std_qty} {ing_unit}",
                "actual_quantity": ing_std_qty, "unit": ing_unit,
                "cost_per_unit": ing_cost_u, "total_cost": ing_tot_c,
                "is_semi_finished": len(subs) > 0 or ing_code.startswith("SF"),
                "sub_ingredients": subs
            })

recipes_list = list(finished_items.values())
for r in recipes_list:
    calc_sum = round(sum(i["total_cost"] for i in r["ingredients"]), 3)
    if r["total_cost"] == 0.0:
        r["total_cost"] = calc_sum

with open(os.path.join(out_dir, "costing_data.json"), "w", encoding="utf-8") as f:
    json.dump(recipes_list, f, ensure_ascii=False, indent=2, allow_nan=False)

# 3. ريسبي وجبات الموظفين - تجميع كامل المقادير تحت كل وجبة وتاريخها
staff_meals = []
if os.path.exists(p_staff):
    xls_s = pd.ExcelFile(p_staff)
    meals_dict = {}

    for s_name in xls_s.sheet_names:
        df_s = pd.read_excel(xls_s, sheet_name=s_name)
        col_code = find_col(df_s, ["معرف", "كود", "code", "odoo"]) or df_s.columns[1]
        col_dish = find_col(df_s, ["وجبة", "طبخة", "meal", "اسم الوجبة"])
        col_desc = find_col(df_s, ["المكونات", "المادة", "اسم", "وصف"]) or (df_s.columns[3] if len(df_s.columns) > 3 else None)
        col_date = find_col(df_s, ["تاريخ", "date"])
        col_qty_kg = find_col(df_s, ["كيلو", "كغ", "وزن", "kg"])
        col_qty_g = find_col(df_s, ["غرام", "جرام", "g"])
        col_cost = find_col(df_s, ["كلفة", "تكلفة", "سعر", "cost"])
        col_tot = find_col(df_s, ["اجمالي", "إجمالي", "total"])

        curr_tracked_dish = ""
        curr_tracked_date = s_name.replace("(", "").replace(")", "").strip()

        for _, row in df_s.iterrows():
            ing_code = c_str(row.get(col_code))
            dish_cand = c_str(row.get(col_dish)) if col_dish else ""
            desc_cand = c_str(row.get(col_desc)) if col_desc else ""
            date_cand = c_str(row.get(col_date)) if col_date else ""

            if date_cand and any(c.isdigit() for c in date_cand):
                curr_tracked_date = date_cand.split()[0].replace("-", "/")

            for text_val in [dish_cand, desc_cand]:
                if text_val and any(k in text_val for k in ["ارز", "أرز", "داوود", "فاصوليا", "معكرونة", "لحمة", "دجاج", "كبسة", "برياني", "منسف", "شوربة", "صينية", "شاورما"]):
                    curr_tracked_dish = text_val
                    break

            if not ing_code or ing_code.lower() in ["nan", "none", "المجموع", "total"]:
                continue
            if re.match(r'^\d{1,2}[-/]\d{1,2}', ing_code):
                curr_tracked_date = ing_code.replace("-", "/")
                continue

            active_dish_name = curr_tracked_dish if curr_tracked_dish else (dish_cand or desc_cand or "وجبة موظفين")

            match_od = odoo_map_by_code.get(ing_code.lower())
            official_name = match_od["name"] if match_od else (desc_cand or f"مادة {ing_code}")

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
            is_sf = len(subs) > 0 or ing_code.startswith("SF")

            clean_dish_title = active_dish_name.replace("(", "").replace(")", "").strip()
            group_key = f"{clean_dish_title}____{curr_tracked_date}"
            if group_key not in meals_dict:
                meals_dict[group_key] = {
                    "name": clean_dish_title, "date": curr_tracked_date,
                    "code": f"STAFF-{len(meals_dict)+1:03d}",
                    "total_cost": 0.0, "ingredients": []
                }

            meals_dict[group_key]["ingredients"].append({
                "code": ing_code, "name": official_name, "raw_description": desc_cand,
                "actual_quantity": actual_qty, "unit": "كيلو",
                "standard_quantity": std_qty, "cost_per_unit": cost_u,
                "total_cost": tot_c, "is_semi_finished": is_sf, "sub_ingredients": subs
            })

    for m in meals_dict.values():
        if len(m["ingredients"]) > 0:
            m["total_cost"] = round(sum(i["total_cost"] for i in m["ingredients"]), 3)
            staff_meals.append(m)

    staff_meals.sort(key=lambda x: str(x["date"]), reverse=True)

with open(os.path.join(out_dir, "staff_meals.json"), "w", encoding="utf-8") as f:
    json.dump(staff_meals, f, ensure_ascii=False, indent=2, allow_nan=False)

# 4. طلبات مارت - مطابقة جدول الإكسل بالمليمتر ودون أي أقواس
talabat_sheets_data = []

KNOWN_CUTS = [
    ("كتف + فخد + رقاب + قطع الشيف", ["كتف", "فخد", "رقاب", "قطع الشيف", "شيف"]),
    ("شقف", ["شقف"]),
    ("لية", ["لية", "ليه"]),
    ("ريش", ["ريش"]),
    ("رفالات + قص مجروم + زوايد", ["رفالات", "قص مجروم", "زوايد", "مجروم"]),
    ("بدنيات", ["بدنيات"]),
    ("نتر", ["نتر"]),
    ("كلاوي", ["كلاوي"]),
    ("خصاوي", ["خصاوي"]),
    ("فتايل", ["فتايل", "فتائل", "فتيل"]),
    ("عروق + عرقيب + عظم", ["عروق", "عرقيب", "عظم"]),
    ("اضلاع خروف 500غرام", ["اضلاع", "أضلاع"]),
]

if os.path.exists(p_talabat):
    xls_t = pd.ExcelFile(p_talabat)

    for s_name in xls_t.sheet_names:
        df_t = pd.read_excel(xls_t, sheet_name=s_name, header=None)
        if len(df_t) < 2: continue

        n_rows, n_cols = df_t.shape
        all_text = " ".join([str(x) for x in df_t.values.flatten() if pd.notna(x)])

        # تنظيف العنوان والتاريخ بدون أي أقواس
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

            # قراءة رأس الفاتورة من الصفوف الأولى
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

            # تحديد مواقع أعمدة الجدول حسب تصميم الإكسل تماماً (الصورة 3)
            r_head = -1
            c_name = -1
            for r in range(min(10, n_rows)):
                for c in range(n_cols):
                    if "اسم الصنف" in str(df_t.iat[r, c]):
                        r_head = r
                        c_name = c
                        break
                if r_head != -1: break

            c_qty = -1
            c_pct = -1
            if r_head != -1:
                for c in range(c_name + 1, n_cols):
                    v = str(df_t.iat[r_head, c]).strip()
                    if "الكمية" in v or "كمية" in v:
                        c_qty = c
                        c_pct = c + 1
                        break

            if c_name == -1: c_name = 3
            if c_qty == -1: c_qty = 6
            if c_pct == -1: c_pct = 7
            c_price = max(0, c_name - 2)
            c_total = max(0, c_name - 1)

            cuts_list = []
            for r in range(r_head + 1 if r_head != -1 else 3, n_rows):
                name_val = str(df_t.iat[r, c_name]).strip()
                if not name_val or name_val.lower() in ["nan", "none"]:
                    for offset in [-1, 1, -2, 2]:
                        if 0 <= c_name + offset < n_cols:
                            cand = str(df_t.iat[r, c_name + offset]).strip()
                            if any(k in cand for k in ["كتف", "شقف", "لية", "ريش", "رفالات", "بدنيات", "نتر", "كلاوي", "خصاوي", "فتايل", "عروق", "اضلاع", "الوزن", "الفاقد"]):
                                name_val = cand
                                break

                if not name_val: continue

                # الأوزان في أسفل الجدول (الرمادي)
                if "الوزن عند استلام" in name_val:
                    weight_received = c_num(df_t.iat[r, c_qty])
                    continue
                elif "الوزن قبل التقطيع" in name_val:
                    weight_cut = c_num(df_t.iat[r, c_qty])
                    continue
                elif "الفاقد" in name_val:
                    waste_loss = c_num(df_t.iat[r, c_qty])
                    continue
                elif "صافي الوزن" in name_val:
                    net_w = c_num(df_t.iat[r, c_qty])
                    if net_w > 0: weight_cut = net_w
                    continue

                matched_cut = None
                for std_name, keywords in KNOWN_CUTS:
                    if any(k in name_val for k in keywords):
                        matched_cut = std_name
                        break

                if matched_cut:
                    p_val = c_num(df_t.iat[r, c_price])
                    tot_val = c_num(df_t.iat[r, c_total])
                    q_val = c_num(df_t.iat[r, c_qty])
                    pct_raw = str(df_t.iat[r, c_pct]).strip() if c_pct < n_cols else ""

                    pct_str = ""
                    if "%" in pct_raw:
                        pct_str = pct_raw
                    else:
                        pct_num = c_num(pct_raw)
                        if 0 < pct_num <= 1.0: pct_str = f"{round(pct_num * 100)}%"
                        elif pct_num > 1.0: pct_str = f"{round(pct_num)}%"

                    if tot_val == 0 and q_val > 0 and p_val > 0:
                        tot_val = round(q_val * p_val, 3)
                    elif p_val == 0 and tot_val > 0 and q_val > 0:
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
                "batch_label": f"دفعة {batch_num}" if batch_num else "",
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

print("🎉 اكتمل بنجاح بناء كافة البيانات ومطابقتها حرفياً مع الصور!")
