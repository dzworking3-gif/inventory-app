import subprocess
import sys

# 0. تثبيت المكاتب تلقائياً إذا لم تكن موجودة
try:
    import openpyxl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام إدارة المخزون والمبيعات المتكامل", layout="wide", page_icon="📦")

# 2. تنسيق شامل وإجبار كافة النصوص للظهور باللون الأبيض الناصع
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    /* تطبيق خط tajawal وتوجيه النص لجميع العناصر */
    * {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
    }

    /* خلفية المستودع */
    .stApp {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.94), rgba(30, 41, 59, 0.96)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=1920&auto=format&fit=crop") !important;
        background-attachment: fixed !important;
        background-size: cover !important;
        background-position: center !important;
        color: #ffffff !important;
    }

    /* 1. إصلاح لون عناوين التبويبات (Tabs) بالكامل */
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] div, button[data-baseweb="tab"] span {
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] p, 
    button[data-baseweb="tab"][aria-selected="true"] div, 
    button[data-baseweb="tab"][aria-selected="true"] span {
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }

    /* 2. إصلاح كافة النصوص والتسميات (Labels) فوق خانات الإدخال */
    label, p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    .stTextInput label p, .stNumberInput label p, .stSelectbox label p, .stFileUploader label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    /* 3. تحسين شكل ولون حقول الإدخال */
    input, textarea, select {
        color: #ffffff !important;
        background-color: #0f172a !important;
    }

    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }

    /* 4. تحسين شكل القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-left: 1px solid #334155;
    }

    /* 5. بطاقات الإحصائيات KPIs */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid #334155 !important;
        border-right: 4px solid #3b82f6 !important;
        padding: 16px !important;
        border-radius: 12px !important;
    }

    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 1rem !important;
    }

    div[data-testid="stMetricValue"] div {
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }

    /* إطارات الاستمارات */
    div[data-testid="stForm"], div.stTabs [data-baseweb="tab-panel"] {
        background: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }

    /* الأزرار */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
    }

    .stButton > button p {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. إنشاء قاعدة البيانات
conn = sqlite3.connect('inventory_system.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                initial_stock REAL,
                price REAL,
                min_limit REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT,
                type TEXT,
                quantity REAL,
                unit_price REAL,
                party_name TEXT,
                date TEXT)''')

conn.commit()

# 4. دالة جلب وحساب بيانات المخزون
def get_inventory():
    df_prod = pd.read_sql_query("SELECT * FROM products", conn)
    df_trans = pd.read_sql_query("SELECT * FROM transactions", conn)
    
    if df_prod.empty:
        return pd.DataFrame(columns=['sku', 'name', 'category', 'initial_stock', 'inputs', 'outputs', 'stock', 'price', 'total_value', 'min_limit', 'status'])
    
    inputs = df_trans[df_trans['type'] == 'إدخال'].groupby('sku')['quantity'].sum().to_dict() if not df_trans.empty else {}
    outputs = df_trans[df_trans['type'] == 'إخراج'].groupby('sku')['quantity'].sum().to_dict() if not df_trans.empty else {}
    
    df_prod['inputs'] = df_prod['sku'].map(inputs).fillna(0)
    df_prod['outputs'] = df_prod['sku'].map(outputs).fillna(0)
    df_prod['stock'] = df_prod['initial_stock'] + df_prod['inputs'] - df_prod['outputs']
    df_prod['total_value'] = df_prod['stock'] * df_prod['price']
    
    def get_status(row):
        if row['stock'] <= 0:
            return '🔴 نفد من المخزون'
        elif row['stock'] <= row['min_limit']:
            return '🟡 منخفض (تحت حد الطلب)'
        return '🟢 متوفر'
        
    df_prod['status'] = df_prod.apply(get_status, axis=1)
    return df_prod

# 5. الواجهة الرئيسية
st.title("📦 نظام إدارة المخزون والمبيعات المتكامل")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 لوحة التحكم", 
    "📦 إدارة المنتجات", 
    "🧾 المبيعات والفواتير", 
    "📥 المشتريات والمدخلات", 
    "📜 سجل الحركة والتقارير"
])

df_inv = get_inventory()

# ==================== Tab 1: لوحة التحكم ====================
with tab1:
    st.subheader("📊 مؤشرات المخزون العامة")
    c1, c2, c3, c4 = st.columns(4)
    
    total_items = len(df_inv)
    total_stock = df_inv['stock'].sum() if not df_inv.empty else 0
    total_val = df_inv['total_value'].sum() if not df_inv.empty else 0
    low_stock = len(df_inv[df_inv['stock'] <= df_inv['min_limit']]) if not df_inv.empty else 0
    
    c1.metric("إجمالي أصناف المنتجات", f"{total_items}")
    c2.metric("إجمالي القطع بالمخزن", f"{total_stock:,.0f}")
    c3.metric("القيمة المالية الإجمالية", f"${total_val:,.2f}")
    c4.metric("منتجات تحت حد الطلب", f"{low_stock}")
    
    st.divider()
    st.subheader("📋 حالة المخزون الحالية")
    if not df_inv.empty:
        st.dataframe(
            df_inv[['sku', 'name', 'category', 'stock', 'price', 'total_value', 'status']],
            column_config={
                "sku": "رقم المنتج (SKU)", "name": "اسم المنتج", "category": "الفئة",
                "stock": "المخزون المتبقي", "price": "السعر ($)", "total_value": "القيمة الإجمالية ($)", "status": "الحالة"
            },
            use_container_width=True, hide_index=True
        )

# ==================== Tab 2: إدارة المنتجات ====================
with tab2:
    col_add, col_file = st.columns([2, 1])
    
    with col_add:
        st.subheader("➕ إضافة / تعديل منتج")
        with st.form("product_form"):
            p_sku = st.text_input("رقم المنتج (SKU)")
            p_name = st.text_input("اسم المنتج")
            p_cat = st.selectbox("الفئة", ["إلكترونيات", "قطع غيار", "أثاث", "عام"])
            p_init = st.number_input("المخزون الأولي", min_value=0.0, value=0.0)
            p_price = st.number_input("سعر الوحدة ($)", min_value=0.0, value=0.0)
            p_min = st.number_input("حد الطلب الأدنى", min_value=0.0, value=5.0)
            
            btn_save = st.form_submit_button("حفظ المنتج")
            if btn_save and p_sku and p_name:
                c.execute('''INSERT INTO products (sku, name, category, initial_stock, price, min_limit)
                             VALUES (?, ?, ?, ?, ?, ?)
                             ON CONFLICT(sku) DO UPDATE SET
                             name=excluded.name, category=excluded.category,
                             price=excluded.price, min_limit=excluded.min_limit''',
                          (p_sku, p_name, p_cat, p_init, p_price, p_min))
                conn.commit()
                st.success("تم حفظ المنتج بنجاح في قاعدة البيانات!")
                st.rerun()

    with col_file:
        st.subheader("📥 استيراد من Excel")
        up_file = st.file_uploader("رفع ملف Excel", type=["xlsx", "csv"])
        if up_file:
            try:
                df_up = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
                for _, row in df_up.iterrows():
                    c.execute('''INSERT INTO products (sku, name, category, initial_stock, price, min_limit)
                                 VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(sku) DO NOTHING''',
                              (str(row['SKU']), str(row['Name']), str(row['Category']), float(row['InitialStock']), float(row['Price']), float(row['MinLimit'])))
                conn.commit()
                st.success("تم استيراد البيانات بنجاح!")
                st.rerun()
            except Exception as e:
                st.error(f"خطأ أثناء التحميل: {e}")

# ==================== Tab 3: المبيعات والفواتير ====================
with tab3:
    st.subheader("🧾 تسجيل عملية بيع / مخرجات")
    if not df_inv.empty:
        with st.form("sale_form"):
            col_s1, col_s2, col_s3 = st.columns(3)
            selected_sku = col_s1.selectbox("اختر المنتج", df_inv['sku'] + " - " + df_inv['name'])
            sku_code = selected_sku.split(" - ")[0]
            
            current_p = df_inv[df_inv['sku'] == sku_code].iloc[0]
            
            qty_out = col_s2.number_input("الكمية المباعة", min_value=1.0, value=1.0)
            client_name = col_s3.text_input("اسم الزبون / الجهة", value="زبون عام")
            
            st.info(f"المخزون المتاح حالياً: {current_p['stock']} | سعر الوحدة: ${current_p['price']}")
            
            btn_sell = st.form_submit_button("تسجيل البيع وإصدار الفاتورة")
            if btn_sell:
                if qty_out > current_p['stock']:
                    st.error("الكمية المطلوبة أكبر من المخزون المتاح!")
                else:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute("INSERT INTO transactions (sku, type, quantity, unit_price, party_name, date) VALUES (?, ?, ?, ?, ?, ?)",
                              (sku_code, 'إخراج', qty_out, current_p['price'], client_name, now))
                    conn.commit()
                    st.success(f"تم تسجيل المبيعات بنجاح للزبون {client_name}!")
                    st.rerun()

# ==================== Tab 4: المشتريات والمدخلات ====================
with tab4:
    st.subheader("📥 تسجيل عملية توريد / مدخلات جديدة")
    if not df_inv.empty:
        with st.form("buy_form"):
            col_b1, col_b2, col_b3 = st.columns(3)
            selected_b_sku = col_b1.selectbox("اختر المنتج لتزويده", df_inv['sku'] + " - " + df_inv['name'])
            b_sku_code = selected_b_sku.split(" - ")[0]
            
            qty_in = col_b2.number_input("الكمية المستلمة", min_value=1.0, value=1.0)
            supplier_name = col_b3.text_input("اسم المورد", value="مورد عام")
            
            btn_buy = st.form_submit_button("إضافة للمخزون")
            if btn_buy:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                unit_p = df_inv[df_inv['sku'] == b_sku_code].iloc[0]['price']
                c.execute("INSERT INTO transactions (sku, type, quantity, unit_price, party_name, date) VALUES (?, ?, ?, ?, ?, ?)",
                          (b_sku_code, 'إدخال', qty_in, unit_p, supplier_name, now))
                conn.commit()
                st.success("تمت إضافة الكميات الجديدة للمخزون بنجاح!")
                st.rerun()

# ==================== Tab 5: السجل والتقارير ====================
with tab5:
    st.subheader("📜 سجل حركة المخزون التاريخي (Ledger)")
    df_history = pd.read_sql_query("""
        SELECT t.id, t.date as 'التاريخ', t.sku as 'رقم المنتج', p.name as 'اسم المنتج', 
               t.type as 'نوع العملية', t.quantity as 'الكمية', t.unit_price as 'سعر الوحدة', 
               (t.quantity * t.unit_price) as 'الإجمالي', t.party_name as 'الطرف الآخر'
        FROM transactions t
        LEFT JOIN products p ON t.sku = p.sku
        ORDER BY t.id DESC
    """, conn)
    
    if not df_history.empty:
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        csv_data = df_history.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل سجل الحركة الكامل (CSV)", data=csv_data, file_name="سجل_حركة_المخزون.csv", mime="text/csv")
    else:
        st.info("لا توجد عمليات مسجلة في السجل بعد.")
