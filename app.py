import subprocess
import sys

# 0. تثبيت المكتبات تلقائياً إذا لم تكن موجودة
try:
    import openpyxl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام إدارة المخزون والمتكامل", layout="wide", page_icon="📦")

# 2. القاموس الخاص باللغات (العربية، الفرنسية، الإنجليزية)
LANGUAGES = {
    "العربية": {
        "title": "📦 نظام إدارة المخزون والمبيعات المتكامل",
        "tabs": ["📊 لوحة التحكم", "📦 إدارة المنتجات", "🧾 المبيعات والفواتير", "📥 المشتريات والمدخلات", "📜 سجل الحركة والتقارير"],
        "kpi1": "إجمالي أصناف المنتجات", "kpi2": "إجمالي القطع بالمخزن", "kpi3": "القيمة المالية الإجمالية", "kpi4": "منتجات تحت حد الطلب",
        "current_stock_title": "📋 حالة المخزون الحالية",
        "sku": "رقم المنتج (SKU)", "name": "اسم المنتج", "category": "الفئة", "stock": "المخزون المتبقي", "price": "السعر ($)", "total_val": "القيمة الإجمالية ($)", "status": "الحالة",
        "add_edit_prod": "➕ إضافة / تعديل منتج", "initial_stock": "المخزون الأولي", "min_limit": "حد الطلب الأدنى", "btn_save_prod": "حفظ المنتج",
        "import_excel": "📥 استيراد من Excel", "file_uploader": "رفع ملف Excel",
        "sale_title": "🧾 تسجيل عملية بيع / مخرجات", "select_prod": "اختر المنتج", "qty_sold": "الكمية المباعة", "client_name": "اسم الزبون / الجهة",
        "stock_available": "المخزون المتاح حالياً", "btn_sell": "تسجيل البيع وإصدار الفاتورة", "err_qty": "الكمية المطلوبة أكبر من المخزون المتاح!",
        "buy_title": "📥 تسجيل عملية توريد / مدخلات جديدة", "select_prod_supply": "اختر المنتج لتزويده", "qty_received": "الكمية المستلمة", "supplier_name": "اسم المورد",
        "btn_buy": "إضافة للمخزون", "history_title": "📜 سجل حركة المخزون التاريخي (Ledger)", "download_csv": "📥 تحميل سجل الحركة الكامل (CSV)",
        "success_prod": "تم حفظ المنتج بنجاح في قاعدة البيانات!", "success_import": "تم استيراد البيانات بنجاح!", "success_sale": "تم تسجيل المبيعات بنجاح للزبون",
        "success_buy": "تمت إضافة الكميات الجديدة للمخزون بنجاح!", "no_history": "لا توجد عمليات مسجلة في السجل بعد."
    },
    "Français": {
        "title": "📦 Système Intégré de Gestion des Stocks et des Ventes",
        "tabs": ["📊 Tableau de Bord", "📦 Gestion des Produits", "🧾 Ventes & Factures", "📥 Achats & Entrées", "📜 Historique & Rapports"],
        "kpi1": "Total des Produits", "kpi2": "Total Articles en Stock", "kpi3": "Valeur Totale", "kpi4": "Produits sous le Seuil",
        "current_stock_title": "📋 État Actuel du Stock",
        "sku": "Réf. Produit (SKU)", "name": "Nom du Produit", "category": "Catégorie", "stock": "Stock Restant", "price": "Prix ($)", "total_val": "Valeur Totale ($)", "status": "Statut",
        "add_edit_prod": "➕ Ajouter / Modifier un Produit", "initial_stock": "Stock Initial", "min_limit": "Seuil d'Alerte", "btn_save_prod": "Enregistrer",
        "import_excel": "📥 Importer depuis Excel", "file_uploader": "Téléverser le fichier Excel",
        "sale_title": "🧾 Enregistrer une Vente / Sortie", "select_prod": "Sélectionner le Produit", "qty_sold": "Quantité Vendue", "client_name": "Nom du Client",
        "stock_available": "Stock Actuel Disponible", "btn_sell": "Enregistrer la Vente", "err_qty": "La quantité demandée dépasse le stock disponible !",
        "buy_title": "📥 Enregistrer un Réapprovisionnement", "select_prod_supply": "Produit à Réapprovisionner", "qty_received": "Quantité Reçue", "supplier_name": "Nom du Fournisseur",
        "btn_buy": "Ajouter au Stock", "history_title": "📜 Historique des Mouvements de Stock (Ledger)", "download_csv": "📥 Télécharger l'historique complet (CSV)",
        "success_prod": "Produit enregistré avec succès !", "success_import": "Données importées avec succès !", "success_sale": "Vente enregistrée avec succès pour le client",
        "success_buy": "Quantités ajoutées au stock avec succès !", "no_history": "Aucun mouvement enregistré pour le moment."
    },
    "English": {
        "title": "📦 Integrated Inventory & Sales Management System",
        "tabs": ["📊 Dashboard", "📦 Product Management", "🧾 Sales & Invoices", "📥 Purchases & Inputs", "📜 History & Reports"],
        "kpi1": "Total Product Items", "kpi2": "Total Pieces in Stock", "kpi3": "Total Financial Value", "kpi4": "Products Below Reorder Point",
        "current_stock_title": "📋 Current Inventory Status",
        "sku": "Product SKU", "name": "Product Name", "category": "Category", "stock": "Remaining Stock", "price": "Price ($)", "total_val": "Total Value ($)", "status": "Status",
        "add_edit_prod": "➕ Add / Edit Product", "initial_stock": "Initial Stock", "min_limit": "Minimum Reorder Limit", "btn_save_prod": "Save Product",
        "import_excel": "📥 Import from Excel", "file_uploader": "Upload Excel File",
        "sale_title": "🧾 Register Sale / Output", "select_prod": "Select Product", "qty_sold": "Sold Quantity", "client_name": "Client / Entity Name",
        "stock_available": "Current Available Stock", "btn_sell": "Register Sale & Issue Invoice", "err_qty": "Requested quantity exceeds available stock!",
        "buy_title": "📥 Register Supply / New Inputs", "select_prod_supply": "Select Product to Restock", "qty_received": "Received Quantity", "supplier_name": "Supplier Name",
        "btn_buy": "Add to Stock", "history_title": "📜 Historical Inventory Ledger", "download_csv": "📥 Download Full Ledger (CSV)",
        "success_prod": "Product successfully saved to database!", "success_import": "Data successfully imported!", "success_sale": "Sale successfully registered for client",
        "success_buy": "New quantities successfully added to stock!", "no_history": "No transactions recorded in the ledger yet."
    }
}

# شريط جانبى لاختيار اللغة
st.sidebar.markdown("### 🌐 اختيار اللغة / Language / Langue")
selected_lang = st.sidebar.selectbox("Language", ["العربية", "Français", "English"], label_visibility="collapsed")
t = LANGUAGES[selected_lang]

# اتجاه الصفحة بناءً على اللغة (RTL للعربية، LTR للفرنسية والإنجليزية)
direction = "rtl" if selected_lang == "العربية" else "ltr"
text_align = "right" if selected_lang == "العربية" else "left"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    * {{
        font-family: 'Tajawal', sans-serif !important;
        direction: {direction};
        text-align: {text_align};
    }}

    .stApp {{
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.94), rgba(30, 41, 59, 0.96)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=1920&auto=format&fit=crop") !important;
        background-attachment: fixed !important;
        background-size: cover !important;
        background-position: center !important;
        color: #ffffff !important;
    }}

    section[data-testid="stFileUploader"] {{
        background-color: #1e293b !important;
        border: 2px dashed #3b82f6 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }}

    section[data-testid="stFileUploader"] * {{
        color: #ffffff !important;
        background-color: transparent !important;
    }}

    section[data-testid="stFileUploader"] button {{
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 6px 16px !important;
        font-weight: bold !important;
    }}

    div[data-testid="stFileUploaderDropzone"] {{
        background-color: #0f172a !important;
        border-radius: 8px !important;
    }}

    button[data-baseweb="tab"] p, button[data-baseweb="tab"] div, button[data-baseweb="tab"] span {{
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }}
    
    button[data-baseweb="tab"][aria-selected="true"] p, 
    button[data-baseweb="tab"][aria-selected="true"] div, 
    button[data-baseweb="tab"][aria-selected="true"] span {{
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }}

    label, p, span, div, h1, h2, h3, h4, h5, h6 {{
        color: #ffffff !important;
    }}

    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] {{
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.95) !important;
    }}

    div[data-testid="stMetric"] {{
        background: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid #334155 !important;
        padding: 16px !important;
        border-radius: 12px !important;
    }}

    div[data-testid="stMetricLabel"] p {{
        color: #94a3b8 !important;
        font-size: 1rem !important;
    }}

    div[data-testid="stMetricValue"] div {{
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }}

    div[data-testid="stForm"], div.stTabs [data-baseweb="tab-panel"] {{
        background: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }}

    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 700 !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
    }}
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
            return '🔴 النفاد / Out'
        elif row['stock'] <= row['min_limit']:
            return '🟡 منخفض / Low'
        return '🟢 متوفر / OK'
        
    df_prod['status'] = df_prod.apply(get_status, axis=1)
    return df_prod

# 5. الواجهة الرئيسية
st.title(t["title"])

tab1, tab2, tab3, tab4, tab5 = st.tabs(t["tabs"])

df_inv = get_inventory()

# ==================== Tab 1: لوحة التحكم ====================
with tab1:
    st.subheader(t["tabs"][0])
    c1, c2, c3, c4 = st.columns(4)
    
    total_items = len(df_inv)
    total_stock = df_inv['stock'].sum() if not df_inv.empty else 0
    total_val = df_inv['total_value'].sum() if not df_inv.empty else 0
    low_stock = len(df_inv[df_inv['stock'] <= df_inv['min_limit']]) if not df_inv.empty else 0
    
    c1.metric(t["kpi1"], f"{total_items}")
    c2.metric(t["kpi2"], f"{total_stock:,.0f}")
    c3.metric(t["kpi3"], f"${total_val:,.2f}")
    c4.metric(t["kpi4"], f"{low_stock}")
    
    st.divider()
    st.subheader(t["current_stock_title"])
    if not df_inv.empty:
        st.dataframe(
            df_inv[['sku', 'name', 'category', 'stock', 'price', 'total_value', 'status']],
            column_config={
                "sku": t["sku"], "name": t["name"], "category": t["category"],
                "stock": t["stock"], "price": t["price"], "total_value": t["total_val"], "status": t["status"]
            },
            use_container_width=True, hide_index=True
        )

# ==================== Tab 2: إدارة المنتجات ====================
with tab2:
    col_add, col_file = st.columns([2, 1])
    
    with col_add:
        st.subheader(t["add_edit_prod"])
        with st.form("product_form"):
            p_sku = st.text_input(t["sku"])
            p_name = st.text_input(t["name"])
            p_cat = st.selectbox(t["category"], ["General / عام", "Electronics / إلكترونيات", "Parts / قطع غيار", "Furniture / أثاث"])
            p_init = st.number_input(t["initial_stock"], min_value=0.0, value=0.0)
            p_price = st.number_input(t["price"], min_value=0.0, value=0.0)
            p_min = st.number_input(t["min_limit"], min_value=0.0, value=5.0)
            
            btn_save = st.form_submit_button(t["btn_save_prod"])
            if btn_save and p_sku and p_name:
                c.execute('''INSERT INTO products (sku, name, category, initial_stock, price, min_limit)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ON CONFLICT(sku) DO UPDATE SET
                           name=excluded.name, category=excluded.category,
                           price=excluded.price, min_limit=excluded.min_limit''',
                          (p_sku, p_name, p_cat, p_init, p_price, p_min))
                conn.commit()
                st.success(t["success_prod"])
                st.rerun()

    with col_file:
        st.subheader(t["import_excel"])
        up_file = st.file_uploader(t["file_uploader"], type=["xlsx", "csv"])
        if up_file:
            try:
                df_up = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
                column_mapping = {
                    'SKU': 'SKU', 'sku': 'SKU',
                    'Name': 'Name', 'name': 'Name',
                    'Category': 'Category', 'category': 'Category',
                    'InitialStock': 'InitialStock', 'stock': 'InitialStock',
                    'Price': 'Price', 'price': 'Price',
                    'MinLimit': 'MinLimit', 'minlimit': 'MinLimit'
                }
                df_up.columns = [str(col).strip() for col in df_up.columns]
                df_up.rename(columns=column_mapping, inplace=True)
                
                for _, row in df_up.iterrows():
                    sku_val = str(row.get('SKU', ''))
                    name_val = str(row.get('Name', 'Product'))
                    cat_val = str(row.get('Category', 'General'))
                    init_val = float(row.get('InitialStock', 0))
                    price_val = float(row.get('Price', 0))
                    min_val = float(row.get('MinLimit', 5))
                    
                    if sku_val and sku_val != 'nan':
                        c.execute('''INSERT INTO products (sku, name, category, initial_stock, price, min_limit)
                                     VALUES (?, ?, ?, ?, ?, ?) 
                                     ON CONFLICT(sku) DO UPDATE SET
                                     name=excluded.name, category=excluded.category,
                                     price=excluded.price, min_limit=excluded.min_limit''',
                                  (sku_val, name_val, cat_val, init_val, price_val, min_val))
                conn.commit()
                st.success(t["success_import"])
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ==================== Tab 3: المبيعات والفواتير ====================
with tab3:
    st.subheader(t["sale_title"])
    if not df_inv.empty:
        with st.form("sale_form"):
            col_s1, col_s2, col_s3 = st.columns(3)
            selected_sku = col_s1.selectbox(t["select_prod"], df_inv['sku'] + " - " + df_inv['name'])
            sku_code = selected_sku.split(" - ")[0]
            current_p = df_inv[df_inv['sku'] == sku_code].iloc[0]
            
            qty_out = col_s2.number_input(t["qty_sold"], min_value=1.0, value=1.0)
            client_name = col_s3.text_input(t["client_name"], value="General Client")
            
            st.info(f"{t['stock_available']}: {current_p['stock']} | {t['price']}: ${current_p['price']}")
            
            btn_sell = st.form_submit_button(t["btn_sell"])
            if btn_sell:
                if qty_out > current_p['stock']:
                    st.error(t["err_qty"])
                else:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute("INSERT INTO transactions (sku, type, quantity, unit_price, party_name, date) VALUES (?, ?, ?, ?, ?, ?)",
                              (sku_code, 'إخراج', qty_out, current_p['price'], client_name, now))
                    conn.commit()
                    st.success(f"{t['success_sale']} {client_name}!")
                    st.rerun()

# ==================== Tab 4: المشتريات والمدخلات ====================
with tab4:
    st.subheader(t["buy_title"])
    if not df_inv.empty:
        with st.form("buy_form"):
            col_b1, col_b2, col_b3 = st.columns(3)
            selected_b_sku = col_b1.selectbox(t["select_prod_supply"], df_inv['sku'] + " - " + df_inv['name'])
            b_sku_code = selected_b_sku.split(" - ")[0]
            
            qty_in = col_b2.number_input(t["qty_received"], min_value=1.0, value=1.0)
            supplier_name = col_b3.text_input(t["supplier_name"], value="General Supplier")
            
            btn_buy = st.form_submit_button(t["btn_buy"])
            if btn_buy:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                unit_p = df_inv[df_inv['sku'] == b_sku_code].iloc[0]['price']
                c.execute("INSERT INTO transactions (sku, type, quantity, unit_price, party_name, date) VALUES (?, ?, ?, ?, ?, ?)",
                          (b_sku_code, 'إدخال', qty_in, unit_p, supplier_name, now))
                conn.commit()
                st.success(t["success_buy"])
                st.rerun()

# ==================== Tab 5: السجل والتقارير ====================
with tab5:
    st.subheader(t["history_title"])
    df_history = pd.read_sql_query("""
        SELECT t.id, t.date as 'Date', t.sku as 'SKU', p.name as 'Product Name', 
               t.type as 'Type', t.quantity as 'Quantity', t.unit_price as 'Unit Price', 
               (t.quantity * t.unit_price) as 'Total', t.party_name as 'Party'
        FROM transactions t
        LEFT JOIN products p ON t.sku = p.sku
        ORDER BY t.id DESC
    """, conn)
    
    if not df_history.empty:
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        csv_data = df_history.to_csv(index=False).encode('utf-8-sig')
        st.download_button(t["download_csv"], data=csv_data, file_name="inventory_ledger.csv", mime="text/csv")
    else:
        st.info(t["no_history"])
