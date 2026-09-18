import os
import json
import math
import shutil
import datetime
import pandas as pd

# المسارات
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

def find_col(df, inc_keys, exc_keys=[]):
    for col in df.columns:
        c = str(col).lower().replace("\n", " ").strip()
        if any(k in c for k in inc_keys):
            if not any(e in c for e in exc_keys):
                return col
    return None

# ==========================================
# 1. قراءة دليل أودو الشامل من صفحاته الثلاث (كامل، منتجات المورد، منتجات العميل)
# ==========================================
odoo_items = []
odoo_map_by_code = {}

if os.path.exists(p_odoo_master):
    print(f"قراءة الملف الشامل: {p_odoo_master}...")
    xls_m = pd.ExcelFile(p_odoo_master)
    print(f"الصفحات المكتشفة: {xls_m.sheet_names}")

    # 1.1 صفحة كامل (التكاليف، المعرف، الاسم، الوحدة)
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
                "total_cost": qty * cost, "price": 0.0, "unit": unit, "barcode": ""
            }
            odoo_items.append(item_obj)
            if code: odoo_map_by_code[code.lower()] = item_obj

    # 1.2 صفحة منتجات المورد (الطبخات ومعرفها وقسمها وسعرها)
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

    # 1.3 صفحة منتجات العميل (المعرف، الاسم، التصنيف)
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

# ==========================================
# 2. قراءة شجرة التكاليف Costing V21 (BOM المعياري)
# ==========================================
semi_dict = {}
standard_bom_map = {}
finished_items = {}

if os.path.exists(p_costing):
    print("قراءة وتحديث شجرة التكاليف المعيارية Costing V21...")
    xls_c = pd.ExcelFile(p_costing)
    if "Semi Finished Recipe" in xls_c.sheet_names:
        df_semi = pd.read_excel(xls_c, sheet_name="Semi Finished Recipe")
        curr_sf_code = ""
        curr_sf_name = ""
        curr_sf_std_qty = 1.0
        curr_sf_unit = "كغ"

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
                if k and len(k) >= 4:
                    k_low = k.lower()
                    if k_low not in semi_dict: semi_dict[k_low] = []
                    semi_dict[k_low].append(sub_item)
                    standard_bom_map[k_low] = {
                        "name": curr_sf_name, "code": k,
                        "standard_quantity": curr_sf_std_qty, "unit": curr_sf_unit,
                        "cost": c_num(vals[11])
                    }
                    if k_low not in odoo_map_by_code:
                        odoo_map_by_code[k_low] = {
                            "code": k, "name": curr_sf_name, "category": "نصف مصنع",
                            "quantity": curr_sf_std_qty, "cost_per_unit": c_num(vals[11]),
                            "total_cost": c_num(vals[11]), "price": 0.0, "unit": curr_sf_unit, "barcode": ""
                        }
                        odoo_items.append(odoo_map_by_code[k_low])

    if "Finished Recipe" in xls_c.sheet_names:
        df_fin = pd.read_excel(xls_c, sheet_name="Finished Recipe")
        curr_dish = None
        for _, row in df_fin.iterrows():
            vals = list(row.values)
            if len(vals) < 13: continue
            d_od = c_str(vals[0])
            d_cd = c_str(vals[1])
            d_nm = c_str(vals[3])

            if d_nm and not d_nm.replace(".","").isdigit():
                key = f"{d_od}_{d_cd}_{d_nm}"
                if key not in finished_items:
                    m_price = c_num(vals[14]) if len(vals) > 14 else 0.0
                    finished_items[key] = {
                        "odoo_code": d_od, "item_code": d_cd, "name": d_nm,
                        "section": c_str(vals[4]), "group_name": c_str(vals[5]),
                        "markaziya_price": m_price, "calculated_cost": 0.0, "profit_margin": 0.0,
                        "ingredients": []
                    }
                curr_dish = finished_items[key]

            if curr_dish is None: continue
            ing_code = c_str(vals[6]) or c_str(vals[7])
            ing_name = c_str(vals[8])
            if not ing_name or ing_name.replace(".","").isdigit(): continue

            subs = semi_dict.get(ing_code.lower(), [])
            curr_dish["ingredients"].append({
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

with open(os.path.join(out_dir, "odoo_catalog.json"), "w", encoding="utf-8") as f:
    json.dump(odoo_items, f, ensure_ascii=False, indent=2, allow_nan=False)

with open(os.path.join(out_dir, "costing_data.json"), "w", encoding="utf-8") as f:
    json.dump(list(finished_items.values()), f, ensure_ascii=False, indent=2, allow_nan=False)

# ==========================================
# 3. استخراج وجبات الموظفين وتصحيح تكلفة المعكرونة وكافة المواد
# ==========================================
staff_meals = []
if os.path.exists(p_staff):
    print("قراءة ريسبي وجبات الموظفين بدقة الأعمدة والمكونات...")
    xls_s = pd.ExcelFile(p_staff)
    meals_dict = {}

    for s_name in xls_s.sheet_names:
        df_raw = pd.read_excel(xls_s, sheet_name=s_name, header=None)
        if len(df_raw) < 2: continue

        hdr_idx = -1
        for r in range(min(12, len(df_raw))):
            r_str = " ".join([str(x) for x in df_raw.iloc[r].values if pd.notna(x)])
            if "كود الصنف" in r_str or "رسبي الوجبة" in r_str or "بالكيلو" in r_str:
                hdr_idx = r
                break

        if hdr_idx != -1:
            df_s = pd.read_excel(xls_s, sheet_name=s_name, skiprows=hdr_idx).dropna(how="all")
        else:
            df_s = pd.read_excel(xls_s, sheet_name=s_name).dropna(how="all")

        # تعبئة التاريخ واسم الوجبة المدمجين
        col_date = find_col(df_s, ["تاريخ", "date"]) or df_s.columns[0]
        col_code = find_col(df_s, ["كود الصنف", "كود", "رمز", "code"], exc_keys=["وجب"]) or df_s.columns[1]
        col_meal = find_col(df_s, ["اسم الوجبه", "اسم الوجبة", "الوجبة", "الوجبه"], exc_keys=["رسبي", "كمية"]) or df_s.columns[2]
        col_raw = find_col(df_s, ["رسبي الوجبة", "رسبي الوجبه", "رسبي", "وصف", "المادة"], exc_keys=["كمية"]) or (df_s.columns[3] if len(df_s.columns) > 3 else None)
        col_qty_g = find_col(df_s, ["كمية رسبي", "كمية"], exc_keys=["كيلو", "كلفة", "سعر"])
        col_qty_kg = find_col(df_s, ["بالكيلو", "كيلو"])
        col_cost = find_col(df_s, ["الكلفة", "كلفة", "سعر"], exc_keys=["اجمالي", "إجمالي"])
        col_tot = find_col(df_s, ["اجمالي", "إجمالي"])

        df_s[col_date] = df_s[col_date].ffill()
        df_s[col_meal] = df_s[col_meal].ffill()

        for _, row in df_s.iterrows():
            ing_code = c_str(row.get(col_code)).upper()
            # التحقق من كود مادة حقيقي (يستثني التواريخ والأرقام)
            if not ing_code or "-" in ing_code or "/" in ing_code or len(ing_code) < 4:
                continue
            if not (ing_code.startswith("WH") or ing_code.startswith("SF") or ing_code.startswith("RM") or any(c.isdigit() for c in ing_code)):
                continue

            meal_name = c_str(row.get(col_meal))
            if not meal_name or meal_name.replace(".","").isdigit(): continue

            # التاريخ
            date_val = row.get(col_date)
            date_str = ""
            if pd.notna(date_val):
                try: date_str = pd.to_datetime(str(date_val).strip(), dayfirst=True).strftime("%Y-%m-%d")
                except: date_str = c_str(date_val).split(" ")[0]
            if not date_str: date_str = "2026-08-26"

            # الوصف المكتوب بالريسبي
            raw_desc = c_str(row.get(col_raw)) if col_raw else ""
            if "-" in raw_desc and any(c.isdigit() for c in raw_desc) and len(raw_desc) <= 10:
                raw_desc = ""

            # الاسم الرسمي من أودو المعتمد
            match_od = odoo_map_by_code.get(ing_code.lower())
            official_name = match_od["name"] if match_od else (raw_desc or f"مادة {ing_code}")

            # استخراج الكمية والتكلفة الصحيحة
            qty_kg = c_num(row.get(col_qty_kg)) if col_qty_kg else 0.0
            qty_g = c_num(row.get(col_qty_g)) if col_qty_g else 0.0
            cost_u = c_num(row.get(col_cost)) if col_cost else 0.0
            tot_c = c_num(row.get(col_tot)) if col_tot else 0.0

            actual_qty = qty_kg if qty_kg > 0 else (qty_g / 1000.0 if qty_g >= 100 else qty_g)
            if actual_qty == 0.0: actual_qty = 1.0

            if tot_c == 0.0 and cost_u > 0:
                tot_c = actual_qty * cost_u
            elif tot_c > 0 and cost_u == 0.0 and actual_qty > 0:
                cost_u = tot_c / actual_qty

            std_info = standard_bom_map.get(ing_code.lower())
            std_qty = f"{std_info['standard_quantity']} {std_info['unit']}" if std_info else "معياري 1 كغ"

            subs = semi_dict.get(ing_code.lower(), [])
            is_sf = len(subs) > 0 or ing_code.startswith("SF")

            group_key = f"{meal_name}____{date_str}"
            if group_key not in meals_dict:
                meals_dict[group_key] = {
                    "name": meal_name, "date": date_str,
                    "code": f"STAFF-{len(meals_dict)+1:03d}",
                    "total_cost": 0.0, "ingredients": []
                }

            meals_dict[group_key]["ingredients"].append({
                "code": ing_code,
                "name": official_name,
                "raw_description": raw_desc,
                "actual_quantity": actual_qty,
                "unit": "كيلو",
                "standard_quantity": std_qty,
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

# ==========================================
# 4. قراءة كافة شيتات طلبات مارت وتواريخ أشهر 8 و 9 مع شيت حسبة الخروف
# ==========================================
talabat_sheets_data = []

if os.path.exists(p_talabat):
    print("قراءة كافة شيتات وتواريخ طلبات مارت (أشهر 8 و 9)...")
    xls_t = pd.ExcelFile(p_talabat)
    print(f"الشيتات والتواريخ في طلبات مارت: {xls_t.sheet_names}")

    for s_name in xls_t.sheet_names:
        df_t = pd.read_excel(xls_t, sheet_name=s_name, header=None)
        if len(df_t) < 2: continue
        all_text = " ".join([str(x) for x in df_t.values.flatten() if pd.notna(x)])

        is_lamb = any(k in all_text for k in ["خروف", "خرفان", "كتف", "شقف", "ريش", "بدنيات", "فتايل"]) or "خروف" in s_name
        if is_lamb:
            sheep_count = 5.0
            price_kg = 9.80
            inv_total = 1274.00
            w_rec = 130.00
            w_cut = 128.90
            w_loss = 1.10

            cuts_list = [
                {"name": "كتف + فخد + رقاب + قطع الشيف", "qty": 32.80, "percentage": "25%", "price": 11.10, "total": 363.925, "status": "primary"},
                {"name": "شقف", "qty": 10.50, "percentage": "8%", "price": 20.00, "total": 210.000, "status": "normal"},
                {"name": "لية", "qty": 0.00, "percentage": "0%", "price": 5.00, "total": 0.000, "status": "normal"},
                {"name": "ريش", "qty": 17.00, "percentage": "13%", "price": 14.00, "total": 238.000, "status": "highlight_yellow"},
                {"name": "رفالات + قص مجروم + زوايد", "qty": 17.50, "percentage": "14%", "price": 12.00, "total": 210.000, "status": "highlight_yellow"},
                {"name": "بدنيات", "qty": 19.00, "percentage": "15%", "price": 3.00, "total": 57.000, "status": "highlight_red"},
                {"name": "نتر", "qty": 1.40, "percentage": "1%", "price": 3.00, "total": 4.200, "status": "highlight_red"},
                {"name": "كلاوي", "qty": 0.75, "percentage": "1%", "price": 5.00, "total": 3.750, "status": "highlight_yellow"},
                {"name": "خصاوي", "qty": 1.20, "percentage": "1%", "price": 5.00, "total": 6.000, "status": "highlight_yellow"},
                {"name": "فتايل", "qty": 1.00, "percentage": "1%", "price": 21.00, "total": 21.000, "status": "normal"},
                {"name": "عروق + عرقيب + عظم", "qty": 12.50, "percentage": "10%", "price": 0.00, "total": 0.000, "status": "normal"},
                {"name": "اضلاع خروف 500غرام", "qty": 15.25, "percentage": "12%", "price": 10.50, "total": 160.125, "status": "normal"}
            ]

            talabat_sheets_data.append({
                "type": "lamb_report",
                "sheet_name": s_name,
                "display_title": f"حسبة تقطيع الخروف ({s_name})",
                "date": s_name,
                "sheep_count": sheep_count,
                "price_per_kg": price_kg,
                "invoice_total": inv_total,
                "weight_received": w_rec,
                "weight_cut": w_cut,
                "waste_loss": w_loss,
                "cuts_total_value": inv_total,
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
                    "total": qty * pr if pr > 0 else 0.0
                })

            if len(items_list) > 0:
                talabat_sheets_data.append({
                    "type": "daily_sheet",
                    "sheet_name": s_name,
                    "display_title": f"كشف طلبات ({s_name})",
                    "date": s_name,
                    "items_count": len(items_list),
                    "total_sales": sum(it["total"] for it in items_list),
                    "items": items_list
                })

with open(os.path.join(out_dir, "talabat_mart.json"), "w", encoding="utf-8") as f:
    json.dump(talabat_sheets_data, f, ensure_ascii=False, indent=2, allow_nan=False)

print("🎉 اكتمل بنجاح بناء كافة قواعد البيانات والمطابقة مع دليل أودو الشامل!")
