import subprocess
import sys

# 0. تثبيت المكاتب تلقائياً إذا لم تكن موجودة
try:
    import openpyxl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])

import streamlit as st
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة المخزون الاحترافي", layout="wide")

# 2. القالب الاحترافي والتصميم (UI CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
        background-color: #0f172a;
        color: #f8fafc;
    }

    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-left: 1px solid #334155;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155 !important;
        border-right: 4px solid #2563eb !important;
        padding: 18px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
        font-weight: 500;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }

    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stForm"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 نظام إدارة وتسيير المخزونات الاحترافي")

# 3. تهيئة قاعدة البيانات في الجلسة (Session State)
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=[
        'رقم المنتج (SKU)', 'اسم المنتج', 'الفئة', 
        'المخزون الأول', 'المدخلات', 'المخرجات', 
        'سعر الوحدة', 'حد الطلب الأدنى'
    ])

# 4. القائمة الجانبية: استيراد وتصدير البيانات (Excel)
st.sidebar.header("📥 إدارة البيانات (Excel)")

uploaded_file = st.sidebar.file_uploader("رفع ملف Excel للمنتجات", type=["xlsx", "xls"])
if uploaded_file is not None:
    try:
        df_uploaded = pd.read_excel(uploaded_file)
        required_cols = ['رقم المنتج (SKU)', 'اسم المنتج', 'الفئة', 'المخزون الأول', 'المدخلات', 'المخرجات', 'سعر الوحدة', 'حد الطلب الأدنى']
        if all(col in df_uploaded.columns for col in required_cols):
            st.session_state.inventory = df_uploaded
            st.sidebar.success("تم تحميل الملف بنجاح!")
        else:
            st.sidebar.error("الملف المرفوع لا يحتوي على الأعمدة المطلوبة.")
    except Exception as e:
        st.sidebar.error(f"حدث خطأ أثناء القراءة: {e}")

if not st.session_state.inventory.empty:
    excel_data = st.session_state.inventory.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button(
        label="📥 تحميل المخزون الحالي (CSV/Excel)",
        data=excel_data,
        file_name="حالة_المخزون.csv",
        mime="text/csv"
    )

# 5. خوارزمية حساب المخزون المتبقي والقيمة المالية
df = st.session_state.inventory.copy()

if not df.empty:
    df['المخزون المتبقي'] = df['المخزون الأول'] + df['المدخلات'] - df['المخرجات']
    df['القيمة الإجمالية'] = df['المخزون المتبقي'] * df['سعر الوحدة']
    
    def check_status(row):
        if row['المخزون المتبقي'] <= 0:
            return '🔴 نفد من المخزون'
        elif row['المخزون المتبقي'] <= row['حد الطلب الأدنى']:
            return '🟡 منخفض (يتطلب طلب)'
        else:
            return '🟢 متوفر'
            
    df['الحالة'] = df.apply(check_status, axis=1)

# 6. عرض مؤشرات الأداء الرئيسية (KPIs)
st.subheader("📊 مؤشرات المخزون العامة")
col1, col2, col3, col4 = st.columns(4)

if not df.empty:
    total_items = len(df)
    total_stock = df['المخزون المتبقي'].sum()
    total_value = df['القيمة الإجمالية'].sum()
    low_stock_count = len(df[df['المخزون المتبقي'] <= df['حد الطلب الأدنى']])

    col1.metric("إجمالي أصناف المنتجات", f"{total_items}")
    col2.metric("إجمالي القطع بالمخزن", f"{total_stock:,.0f}")
    col3.metric("القيمة المالية الإجمالية", f"${total_value:,.2f}")
    col4.metric("منتجات تحت حد الطلب", f"{low_stock_count}", delta_color="inverse")
else:
    st.info("لا توجد بيانات مخزون حالية. قم بإضافة منتجات أو رفع ملف Excel.")

st.divider()

# 7. إضافة / تحديث منتج يدويًا
with st.expander("➕ إضافة أو تحديث منتج يدويًا"):
    with st.form("add_product_form"):
        c1, c2, c3 = st.columns(3)
        sku = c1.text_input("رقم المنتج (SKU)")
        name = c2.text_input("اسم المنتج")
        category = c3.selectbox("الفئة", ["إلكترونيات", "أثاث", "قطع غيار", "مستلزمات عامة"])

        c4, c5, c6 = st.columns(3)
        initial = c4.number_input("المخزون الأول", min_value=0, value=0)
        inputs = c5.number_input("المدخلات الجديدة", min_value=0, value=0)
        outputs = c6.number_input("المخرجات (المبيعات/السحب)", min_value=0, value=0)

        c7, c8 = st.columns(2)
        price = c7.number_input("سعر الوحدة", min_value=0.0, value=0.0, step=0.5)
        min_limit = c8.number_input("حد الطلب الأدنى (Reorder Point)", min_value=0, value=5)

        submit = st.form_submit_button("حفظ / تحديث المنتج")

        if submit and sku and name:
            new_data = {
                'رقم المنتج (SKU)': sku, 'اسم المنتج': name, 'الفئة': category,
                'المخزون الأول': initial, 'المدخلات': inputs, 'المخرجات': outputs,
                'سعر الوحدة': price, 'حد الطلب الأدنى': min_limit
            }
            if sku in st.session_state.inventory['رقم المنتج (SKU)'].values:
                st.session_state.inventory.loc[st.session_state.inventory['رقم المنتج (SKU)'] == sku] = new_data
            else:
                st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_data])], ignore_index=True)
            st.success(f"تم حفظ المنتج {name} بنجاح!")
            st.rerun()

# 8. عرض جدول المخزون التفصيلي
st.subheader("📋 جدول المخزون التفصيلي")
if not df.empty:
    search_term = st.text_input("🔍 بحث باسم المنتج أو الرقم (SKU):")
    if search_term:
        df_filtered = df[df['اسم المنتج'].str.contains(search_term, na=False) | df['رقم المنتج (SKU)'].str.contains(search_term, na=False)]
    else:
        df_filtered = df

    st.dataframe(
        df_filtered,
        column_config={
            "القيمة الإجمالية": st.column_config.NumberColumn(format="$%.2f"),
            "سعر الوحدة": st.column_config.NumberColumn(format="$%.2f"),
            "المخزون المتبقي": st.column_config.NumberColumn(format="%d"),
        },
        use_container_width=True,
        hide_index=True
    )
