import streamlit as st
import pandas as pd
import numpy as np

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة المخزون الاحترافي", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stMetric { text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("📦 نظام إدارة وتسيير المخزونات الاحترافي")

# 2. القائمة الجانبية: رفع ملفات Excel
st.sidebar.header("لوحة التسيير واستيراد البيانات ⚙️")

uploaded_file = st.sidebar.file_uploader("رفع/تحديث عبر Excel", type=["xlsx", "xls", "csv"])

if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame()

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_uploaded = pd.read_csv(uploaded_file)
        else:
            df_uploaded = pd.read_excel(uploaded_file)
            
        df_uploaded.columns = df_uploaded.columns.str.strip()
        
        # خريطة لتوحيد أسماء الأعمدة بالعربية أو الإنجليزية
        col_map = {
            'sku': 'الكود',
            'name': 'اسم المنتج / المادة',
            'category': 'الفئة',
            'initial_stock': 'م. الأول',
            'inputs': '(+) المدخلات',
            'outputs': '(-) المخرجات',
            'unit_price': 'سعر الوحدة (د.ج)',
            'min_limit': 'حد الطلب الأدنى'
        }
        df_uploaded = df_uploaded.rename(columns=col_map)
        st.session_state.inventory = df_uploaded
        st.sidebar.success("تم تحميل الملف بنجاح!")
    except Exception as e:
        st.sidebar.error(f"حدث خطأ أثناء تحميل الملف: {e}")

# 3. معالجة وتنظيف البيانات
if not st.session_state.inventory.empty:
    df = st.session_state.inventory.copy()

    # إكمال الأعمدة الناقصة إن وجدت
    expected_cols = ['الكود', 'اسم المنتج / المادة', 'الفئة', 'م. الأول', '(+) المدخلات', '(-) المخرجات', 'سعر الوحدة (د.ج)', 'حد الطلب الأدنى']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0 if col not in ['الكود', 'اسم المنتج / المادة', 'الفئة'] else '-'

    # تحويل القيم الفارغة (None / NaN) إلى صفر للأعداد
    num_cols = ['م. الأول', '(+) المدخلات', '(-) المخرجات', 'سعر الوحدة (د.ج)', 'حد الطلب الأدنى']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # خوارزميات الحساب الآلي
    # المخزون الباقي = م. الأول + المدخلات - المخرجات
    df['المخزون الباقي'] = df['م. الأول'] + df['(+) المدخلات'] - df['(-) المخرجات']
    df['القيمة الإجمالية (د.ج)'] = df['المخزون الباقي'] * df['سعر الوحدة (د.ج)']

    # تحديد الحالة تلقائياً
    def get_status(row):
        if row['المخزون الباقي'] <= 0:
            return '🔴 نفد من المخزون'
        elif row['المخزون الباقي'] <= row['حد الطلب الأدنى']:
            return '🟡 منخفض'
        else:
            return '🟢 متوفر'

    df['الحالة'] = df.apply(get_status, axis=1)

    # ترتيب الأعمدة للعرض
    display_cols = [
        'الكود', 'اسم المنتج / المادة', 'الفئة', 'م. الأول', 
        '(+) المدخلات', '(-) المخرجات', 'المخزون الباقي', 
        'سعر الوحدة (د.ج)', 'حد الطلب الأدنى', 'الحالة'
    ]

    # 4. عرض الجدول التفاعلي
    st.subheader("📋 جدول المواد والمخزون")
    
    edited_df = st.data_editor(
        df[display_cols],
        column_config={
            "سعر الوحدة (د.ج)": st.column_config.NumberColumn(format="%.2f د.ج"),
            "المخزون الباقي": st.column_config.NumberColumn(disabled=True),
            "الحالة": st.column_config.TextColumn(disabled=True),
        },
        use_container_width=True,
        hide_index=True
    )

    if st.button("💾 حفظ كل التعديلات في قاعدة البيانات", type="primary"):
        st.session_state.inventory = edited_df
        st.success("تم حفظ التعديلات بنجاح!")
        st.rerun()

    # 5. التقييم المالي
    st.subheader("💰 التقييم المالي الإجمالي")
    total_val = df['القيمة الإجمالية (د.ج)'].sum()
    st.metric("إجمالي قيمة المخزون الحالي", f"{total_val:,.2f} د.ج")

else:
    st.info("يرجى رفع ملف Excel يحتوي على بيانات المواد لبدء العرض الحسابي.")
