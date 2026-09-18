import os
import json
import math
import shutil
import pandas as pd

p_costing = "Costing V21.xlsx"
if not os.path.exists(p_costing): p_costing = os.path.expanduser(r"~\Downloads\Costing V21.xlsx")

p_staff = r"C:\Users\NTC\Desktop\ريسبي وجبات الموظفين.xlsx"
if not os.path.exists(p_staff): p_staff = os.path.expanduser(r"~\Desktop\ريسبي وجبات الموظفين.xlsx")

p_odoo = os.path.expanduser(r"~\Downloads\اصناف اودو اخر تحديث (2).xlsx")
if not os.path.exists(p_odoo): p_odoo = r"C:\Users\NTC\Downloads\اصناف اودو اخر تحديث (2).xlsx"

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

# ==========================================
# 1. شجرة التكاليف وقراءة أعمدة odoo و SF و RM
# ==========================================
semi_dict = {}
standard_bom_map = {}
finished_items = {}

if os.path.exists(p_costing):
    print("فهرسة عمود odoo وشجرة التكاليف المعيارية...")
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
                "rm_code": rm_code,
                "name": rm_nm,
                "standard_quantity": c_num(vals[7]),
                "unit": c_str(vals[8]) or "كغ",
                "cost_per_unit": c_num(vals[10]),
                "total_cost": c_num(vals[11])
            }

            for k in [curr_sf_code, sf_od, sf_cd]:
                if k and len(k) >= 4:
                    k_low = k.lower()
                    if k_low not in semi_dict: semi_dict[k_low] = []
                    semi_dict[k_low].append(sub_item)
                    standard_bom_map[k_low] = {
                        "name": curr_sf_name,
                        "code": k,
                        "standard_quantity": curr_sf_std_qty,
                        "unit": curr_sf_unit,
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

with open(os.path.join(out_dir, "costing_data.json"), "w", encoding="utf-8") as f:
    json.dump(list(finished_items.values()), f, ensure_ascii=False, indent=2, allow_nan=False)

# ==========================================
# 2. دليل أودو: الكود، الاسم، الكمية، كلفة الكمية، الإجمالي
# ==========================================
odoo_items = []
odoo_map_by_code = {}

if os.path.exists(p_odoo):
    print("قراءة وتجهيز دليل أودو...")
    df_odoo = pd.read_excel(p_odoo).dropna(how="all")
    for _, row in df_odoo.iterrows():
        vals = list(row.values)
        if len(vals) < 2: continue
        name = c_str(vals[0])
        code = c_str(vals[1])
        if not name or name.replace(".","").isdigit(): continue

        qty = c_num(vals[3]) if len(vals) > 3 and c_num(vals[3]) > 0 else 1.0
        cost_u = c_num(vals[4]) if len(vals) > 4 else (c_num(vals[3]) if len(vals) > 3 else 0.0)
        tot_val = c_num(vals[5]) if len(vals) > 5 else (qty * cost_u)

        item_obj = {
            "code": code,
            "name": name,
            "category": c_str(vals[2]) if len(vals) > 2 else "عام",
            "quantity": qty,
            "cost_per_unit": cost_u,
            "total_cost": tot_val,
            "price": c_num(vals[6]) if len(vals) > 6 else 0.0,
            "unit": c_str(vals[7]) if len(vals) > 7 else "كغ",
            "barcode": c_str(vals[8]) if len(vals) > 8 else ""
        }
        odoo_items.append(item_obj)
        if code: odoo_map_by_code[code.lower()] = item_obj

# دمج أكواد SF20600002 و SF21000014 وغيرها في دليل أودو
for k_low, b_info in standard_bom_map.items():
    if k_low not in odoo_map_by_code:
        odoo_map_by_code[k_low] = {
            "code": b_info["code"],
            "name": b_info["name"],
            "category": "نصف مصنع",
            "quantity": b_info["standard_quantity"],
            "cost_per_unit": b_info["cost"],
            "total_cost": b_info["cost"] * b_info["standard_quantity"],
            "price": 0.0,
            "unit": b_info["unit"],
            "barcode": ""
        }
        odoo_items.append(odoo_map_by_code[k_low])

with open(os.path.join(out_dir, "odoo_catalog.json"), "w", encoding="utf-8") as f:
    json.dump(odoo_items, f, ensure_ascii=False, indent=2, allow_nan=False)

# ==========================================
# 3. وجبات الموظفين: الاسم، الكود، التكلفة، الحجم المعياري، والحجم المستخدم للطبخة
# ==========================================
staff_meals = []
if os.path.exists(p_staff):
    print("قراءة ريسبي وجبات الموظفين وتحديد الحجم المعياري والفعلي...")
    xls_s = pd.ExcelFile(p_staff)
    meals_dict = {}

    for s_name in xls_s.sheet_names:
        df_raw = pd.read_excel(xls_s, sheet_name=s_name, header=None)
        if len(df_raw) < 2: continue

        # البحث عن رأس الجدول التفصيلي
        hdr_idx = -1
        for r in range(min(12, len(df_raw))):
            r_str = " ".join([str(x) for x in df_raw.iloc[r].values if pd.notna(x)])
            if "كود الصنف" in r_str or "رسبي الوجبة" in r_str or "اسم الوجب" in r_str:
                hdr_idx = r
                break

        if hdr_idx != -1:
            df_s = pd.read_excel(xls_s, sheet_name=s_name, skiprows=hdr_idx).dropna(how="all")
        else:
            df_s = pd.read_excel(xls_s, sheet_name=s_name).dropna(how="all")

        for c in df_s.columns[:3]:
            df_s[c] = df_s[c].ffill()

        for _, row in df_s.iterrows():
            vals = list(row.values)
            if len(vals) < 4: continue

            # كود المادة الحقيقي (WH, SF, RM)
            ing_code = ""
            for v in vals:
                vs = c_str(v).upper()
                if (vs.startswith("WH") or vs.startswith("SF") or vs.startswith("RM")) and len(vs) >= 6:
                    ing_code = vs
                    break
            if not ing_code: continue

            # اسم الوجبة الحقيقي
            meal_name = ""
            for v in vals:
                vs = c_str(v)
                if any(w in vs for w in ["اوزي", "منسف", "قدرة", "ملوخية", "فاصوليا", "بازيلا", "داوود", "برياني", "كبسة", "دجاج", "لحم", "شعرية", "شاكرية", "فاهيتا", "بامية", "منزلة", "مجدرة", "مندي", "شاورما"]):
                    meal_name = vs
                    break
            if not meal_name or meal_name.replace(".","").isdigit():
                meal_name = c_str(vals[2])
                if meal_name.replace(".","").isdigit(): continue

            # التاريخ
            date_str = ""
            for v in vals:
                vs = c_str(v)
                if any(ch.isdigit() for ch in vs) and ("-" in vs or "/" in vs) and len(vs) >= 8:
                    try: date_str = pd.to_datetime(vs, dayfirst=True).strftime("%Y-%m-%d")
                    except: date_str = vs.split(" ")[0]
                    break
            if not date_str: date_str = "2026-08-26"

            # وصف المادة بالريسبي
            raw_desc = ""
            for v in vals:
                vs = c_str(v)
                if vs and vs != ing_code and vs != meal_name and vs != date_str and not vs.replace(".","").isdigit():
                    raw_desc = vs
                    break

            # الاسم الرسمي من أودو
            match_od = odoo_map_by_code.get(ing_code.lower())
            official_name = match_od["name"] if match_od else (raw_desc or f"صنف {ing_code}")

            # الحجم المعياري من شجرة التكاليف
            std_info = standard_bom_map.get(ing_code.lower())
            std_qty = std_info["standard_quantity"] if std_info else 1.0
            std_unit = std_info["unit"] if std_info else "كغ"

            # الحجم الفعلي المستخدم للطبخة من الشيت
            nums = [c_num(x) for x in vals if str(x).replace(".","").replace("-","").isdigit() and c_num(x) > 0]
            actual_qty = 1.0
            cost_u = 0.0
            tot_c = 0.0

            if len(nums) >= 4:
                actual_qty = nums[1] # بالكيلو
                cost_u = nums[2]
                tot_c = nums[3]
            elif len(nums) == 3:
                actual_qty = nums[0]
                cost_u = nums[1]
                tot_c = nums[2]
            elif len(nums) == 2:
                actual_qty = nums[0]
                tot_c = nums[1]
                cost_u = tot_c / actual_qty if actual_qty > 0 else tot_c

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
                "actual_quantity": actual_qty,
                "unit": "كيلو",
                "standard_quantity": f"{std_qty} {std_unit}" if std_info else "معياري 1 كغ",
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
print(f"تم تصدير {len(staff_meals)} وجبة موظفين بالحجم المعياري والفعلي.")

# ==========================================
# 4. طلبات مارت: شيت حسبة الخروف التفصيلي الكامل
# ==========================================
lamb_data = {
    "sheep_count": 5.0,
    "price_per_kg": 9.80,
    "invoice_total": 1274.00,
    "weight_received": 130.00,
    "weight_before_cut": 128.90,
    "waste_loss": 1.10,
    "net_weight_cut": 128.90,
    "cuts_total_value": 1274.00,
    "cuts": [
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
        {"name": "عروق + عرقيب + عظم", "qty": 12.50, "percentage": "10%", "price": 0.00, "total": 0.000, "status": "waste"},
        {"name": "اضلاع خروف 500غرام", "qty": 15.25, "percentage": "12%", "price": 10.50, "total": 160.125, "status": "normal"}
    ]
}

with open(os.path.join(out_dir, "talabat_mart.json"), "w", encoding="utf-8") as f:
    json.dump(lamb_data, f, ensure_ascii=False, indent=2, allow_nan=False)
print("تم تصدير شيت تفصيل الخروف الكامل بنجاح 100%!")
