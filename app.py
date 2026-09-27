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
import io
from datetime import datetime

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام إدارة المخزون والمبيعات المتكامل", layout="wide", page_icon="📦")

# 2. القاموس الخاص باللغات
LANGUAGES = {
    "العربية": {
        "title": "📦 نظام إدارة المخزون والمبيعات المتكامل",
        "tabs": ["📊 لوحة التحكم", "📦 إدارة المنتجات", "🧾 المبيعات والفواتير", "📥 المشتريات والمدخلات", "📜 سجل الحركة والتقارير", "⚙️ إعدادات الشركة والأرقام"],
        "kpi1": "إجمالي أصناف المنتجات", "kpi2": "إجمالي القطع بالمخزن", "kpi3": "القيمة المالية الإجمالية", "kpi4": "منتجات تحت حد الطلب",
        "current_stock_title": "📋 حالة المخزون الحالية",
        "sku": "رقم المنتج (SKU)", "name": "اسم المنتج", "category": "الفئة", "stock": "المخزون المتبقي", "price": "السعر ($)", "total_val": "القيمة الإجمالية ($)", "status": "الحالة",
        "add_edit_prod": "➕ إضافة أو تعديل منتج", "initial_stock": "المخزون الأولي", "min_limit": "حد الطلب الأدنى", "btn_save_prod": "حفظ / تحديث المنتج في النظام",
        "import_excel": "📥 استيراد من Excel", "file_uploader": "رفع ملف Excel",
        "sale_title": "🧾 تسجيل عملية بيع / مخرجات", "select_prod": "اختر المنتج", "qty_sold": "الكمية المباعة", "client_name": "اسم الزبون / الجهة",
        "stock_available": "المخزون المتاح حالياً", "btn_sell": "تسجيل البيع وإصدار الفاتورة", "err_qty": "الكمية المطلوبة أكبر من المخزون المتاح!",
        "buy_title": "📥 تسجيل عملية توريد / مدخلات جديدة", "select_prod_supply": "اختر المنتج لتزويده", "qty_received": "الكمية المستلمة", "supplier_name": "اسم المورد",
        "btn_buy": "إضافة للمخزون", "history_title": "📜 سجل حركة المخزون التاريخي (Ledger)", 
        "download_excel": "📥 تحميل ملف Excel للمخزون", "download_history_excel": "📥 تحميل سجل الحركات (Excel)",
        "success_prod": "تم حفظ / تحديث المنتج بنجاح في قاعدة البيانات!", "success_import": "تم استيراد البيانات بنجاح!", "success_sale": "تم تسجيل المبيعات بنجاح للزبون",
        "success_buy": "تمت إضافة الكميات الجديدة للمخزون بنجاح!", "no_history": "لا توجد عمليات مسجلة في السجل بعد.",
        "settings_title": "⚙️ إعدادات الشركة وبيانات التواصل والأرقام التعريفية",
        "comp_name": "اسم المؤسسة / الشركة", "comp_phone": "رقم الهاتف / النقال", "comp_tax": "الرقم الضريبي / السجل التجاري", "comp_address": "العنوان",
        "btn_save_settings": "حفظ الإعدادات التعريفية", "success_settings": "تم حفظ الإعدادات بنجاح!",
        "edit_mode_label": "تعديل منتج موجود مسبقاً؟"
    },
    "Français": {
        "title": "📦 Système de Gestion des Stocks et des Ventes",
        "tabs": ["📊 Tableau de Bord", "📦 Gestion des Produits", "🧾 Ventes & Factures", "📥 Achats & Entrées", "📜 Historique & Rapports", "⚙️ Paramètres"],
        "kpi1": "Total des Produits", "kpi2": "Articles en Stock", "kpi3": "Valeur Totale", "kpi4": "Produits sous Seuil",
        "current_stock_title": "📋 État Actuel du Stock",
        "sku": "Réf. Produit (SKU)", "name": "Nom du Produit", "category": "Catégorie", "stock": "Stock Restant", "price": "Prix ($)", "total_val": "Valeur Totale ($)", "status": "Statut",
        "add_edit_prod": "➕ Ajouter ou Modifier un Produit", "initial_stock": "Stock Initial", "min_limit": "Seuil d'Alerte", "btn_save_prod": "Enregistrer / Mettre à jour",
        "import_excel": "📥 Importer depuis Excel", "file_uploader": "Téléverser le fichier Excel",
        "sale_title": "🧾 Enregistrer une Vente / Sortie", "select_prod": "Sélectionner le Produit", "qty_sold": "Quantité Vendue", "client_name": "Nom du Client",
        "stock_available": "Stock Actuel Disponible", "btn_sell": "Enregistrer la Vente", "err_qty": "La quantité demandée dépasse le stock disponible !",
        "buy_title": "📥 Enregistrer un Réapprovisionnement", "select_prod_supply": "Produit à Réapprovisionner", "qty_received": "Quantité Reçue", "supplier_name": "Nom du Fournisseur",
        "btn_buy": "Ajouter au Stock", "history_title": "📜 Historique des Mouvements de Stock", 
        "download_excel": "📥 Télécharger le fichier Excel du stock", "download_history_excel": "📥 Télécharger l'historique",
        "success_prod": "Produit enregistré / mis à jour avec succès !", "success_import": "Données importées avec succès !", "success_sale": "Vente enregistrée avec succès pour le client",
        "success_buy": "Quantités ajoutées au stock avec succès !", "no_history": "Aucun mouvement enregistré pour le moment.",
        "settings_title": "⚙️ Paramètres de l'Entreprise et Coordonnées",
        "comp_name": "Nom de l'Entreprise", "comp_phone": "Numéro de Téléphone", "comp_tax": "Numéro Fiscal / Registre", "comp_address": "Adresse",
        "btn_save_settings": "Enregistrer les Paramètres", "success_settings": "Paramètres enregistrés avec succès !",
        "edit_mode_label": "Modifier un produit existant ?"
    },
    "English": {
        "title": "📦 Integrated Inventory & Sales System",
        "tabs": ["📊 Dashboard", "📦 Products", "🧾 Sales & Invoices", "📥 Purchases", "📜 History & Reports", "⚙️ Settings"],
        "kpi1": "Total Products", "kpi2": "Pieces in Stock", "kpi3": "Total Value", "kpi4": "Low Stock Products",
        "current_stock_title": "📋 Current Inventory Status",
        "sku": "Product SKU", "name": "Product Name", "category": "Category", "stock": "Remaining Stock", "price": "Price ($)", "total_val": "Total Value ($)", "status": "Status",
        "add_edit_prod": "📦 Add or Edit Product", "initial_stock": "Initial Stock", "min_limit": "Minimum Limit", "btn_save_prod": "Save / Update Product",
        "import_excel": "📥 Import from Excel", "file_uploader": "Upload Excel File",
        "sale_title": "🧾 Register Sale / Output", "select_prod": "Select Product", "qty_sold": "Sold Quantity", "client_name": "Client Name",
        "stock_available": "Current Available Stock", "btn_sell": "Register Sale", "err_qty": "Requested quantity exceeds available stock!",
        "buy_title": "📥 Register Supply / New Inputs", "select_prod_supply": "Select Product to Restock", "qty_received": "Received Quantity", "supplier_name": "Supplier Name",
        "btn_buy": "Add to Stock", "history_title": "📜 Historical Inventory Ledger", 
        "download_excel": "📥 Download Excel File", "download_history_excel": "📥 Download Ledger",
        "success_prod": "Product successfully saved / updated!", "success_import": "Data successfully imported!", "success_sale": "Sale successfully registered for client",
        "success_buy": "New quantities successfully added to stock!", "no_history": "No transactions recorded yet.",
        "settings_title": "⚙️ Company Settings & Info",
        "comp_name": "Company Name", "comp_phone": "Phone Number", "comp_tax": "Tax ID / Register", "comp_address": "Address",
        "btn_save_settings": "Save Settings", "success_settings": "Settings successfully saved!",
        "edit_mode_label": "Edit existing product?"
    }
}

selected_lang = st.sidebar.selectbox("Language / Langue", ["العربية", "Français", "English"], label_visibility="collapsed")
t = LANGUAGES[selected_lang]

# تحديد الاتجاه تلقائياً
direction = "rtl" if selected_lang == "العربية" else "ltr"
text_align = "right" if selected_lang == "العربية" else "left"

# 3. تنسيق CSS مُحسّن ومضبوط لإزالة التداخل نهائياً
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    * {{
        font-family: 'Tajawal', sans-serif !important;
    }}

    /* إلغاء تداخل الشريط العلوي تماماً ودفع المحتوى للأسفل */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        position: relative !important;
        height: 50px !important;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }}

    /* إبعاد عناصر القائمة الجانبية وحجب أيقونة الطي المتداخلة */
    section[data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.98) !important;
        border-right: 1px solid #1e293b;
        padding-top: 4rem !important;
    }}

    .stApp {{
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.98)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=1920&auto=format&fit=crop") !important;
        background-attachment: fixed !important;
        background-size: cover !important;
        background-position: center !important;
        color: #f8fafc !important;
        direction: {direction} !important;
        text-align: {text_align} !important;
    }}

    h1 {{
        margin-top: 0px !important;
        padding-top: 0px !important;
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
    }}

    input, textarea, select, 
    div[data-baseweb="select"] > div, 
    div[data-baseweb="base-input"] {{
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border-color: #334155 !important;
        text-align: {text_align} !important;
    }}

    div[data-baseweb="popover"], 
    div[data-baseweb="menu"], 
    ul[data-baseweb="menu"],
    div[role="listbox"],
    ul[role="listbox"] {{
        background-color: #0f172a !important;
        color: #f8fafc !important;
        text-align: {text_align} !important;
    }}

    li[data-baseweb="option"], 
    div[data-baseweb="option"],
    div[role="option"],
    li[role="option"] {{
        background-color: #0f172a !important;
        color: #f8fafc !important;
        text-align: {text_align} !important;
    }}

    li[data-baseweb="option"]:hover, 
    div[data-baseweb="option"]:hover,
    div[role="option"]:hover,
    li[role="option"]:hover {{
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }}

    div[data-testid="stFileUploader"] {{
        background-color: #0f172a !important;
        border: 2px dashed #3b82f6 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        text-align: center !important;
    }}

    div[data-testid="stFileUploader"] section, 
    div[data-testid="stFileUploader"] div, 
    div[data-testid="stFileUploader"] span, 
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploaderDropzone"] {{
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }}

    div.stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 10px;
    }}

    button[data-baseweb="tab"] {{
        background-color: transparent !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
    }}
    
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] div, button[data-baseweb="tab"] span {{
        color: #94a3b8 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }}
    
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: #2563eb !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] p, 
    button[data-baseweb="tab"][aria-selected="true"] div, 
    button[data-baseweb="tab"][aria-selected="true"] span {{
        color: #ffffff !important;
        font-weight: 800 !important;
    }}

    label, p, span, div, h2, h3, h4, h5, h6 {{
        color: #f8fafc !important;
        text-align: {text_align} !important;
    }}

    div[data-testid="stMetric"] {{
        background: rgba(30, 41, 59, 0.85) !important;
        border: 1px solid #334155 !important;
        padding: 16px !important;
        border-radius: 12px !important;
        text-align: center !important;
    }}

    div[data-testid="stMetricLabel"] p {{
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        text-align: center !important;
    }}

    div[data-testid="stMetricValue"] div {{
        color: #38bdf8 !important;
        font-weight: 800 !important;
        text-align: center !important;
    }}

    div[data-testid="stForm"], div.stTabs [data-baseweb="tab-panel"] {{
        background: rgba(30, 41, 59, 0.85) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        margin-top: 10px !important;
    }}

    .stButton > button, div[data-testid="stDownloadButton"] > button {{
        border-radius: 8px !important;
        font-weight: 700 !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        width: 100% !important;
        padding: 0.6rem 1rem !important;
        transition: 0.3s;
    }}
    
    .stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {{
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
    }}
    </style>
""", unsafe_allow_html=True)

# 4. قاعدة البيانات (إعداد الجداول)
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

c.execute('''CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT)''')

conn.commit()

def get_setting(key, default=""):
    res = c.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return res[0] if res else default

def save_setting(key, value):
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()

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
            return '🔴 نفد / Out'
        elif row['stock'] <= row['min_limit']:
            return '🟡 منخفض / Low'
        return '🟢 متوفر / OK'
        
    df_prod['status'] = df_prod.apply(get_status, axis=1)
    return df_prod

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# 5. الواجهة الرئيسية
st.title(t["title"])

comp_name_val = get_setting("comp_name", "")
comp_phone_val = get_setting("comp_phone", "")
if comp_name_val:
    st.caption(f"🏢 **{comp_name_val}** | 📞 {comp_phone_val}")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(t["tabs"])
df_inv = get_inventory()

# ==================== Tab 1: لوحة التحكم ====================
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    
    total_items = len(df_inv)
    total_stock = df_inv['stock'].sum() if not df_inv.empty else 0
    total_val = df_inv['total_value'].sum() if not df_inv.empty else 0
    low_stock = len(df_inv[df_inv['stock'] <= df_inv['min_limit']]) if not df_inv.empty else 0
    
    c1.metric(t["kpi1"], f"{total_items}")
    c2.metric(t["kpi2"], f"{total_stock:,.0f}")
    c3.metric(t["kpi3"], f"${total_val:,.2f}")
    c4.metric(t["kpi4"], f"{low_stock}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_title, col_btn = st.columns([3, 1])
    col_title.subheader(t["current_stock_title"])
    
    if not df_inv.empty:
        with col_btn:
            excel_file = to_excel(df_inv)
            st.download_button(
                label=t["download_excel"],
                data=excel_file,
                file_name="inventory_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.dataframe(
            df_inv[['sku', 'name', 'category', 'stock', 'price', 'total_value', 'status']],
            column_config={
                "sku": t["sku"], "name": t["name"], "category": t["category"],
                "stock": st.column_config.NumberColumn(format="%.0f"), 
                "price": st.column_config.NumberColumn(format="$%.2f"), 
                "total_value": st.column_config.NumberColumn(format="$%.2f"), 
                "status": t["status"]
            },
            use_container_width=True, hide_index=True
        )

# ==================== Tab 2: إدارة المنتجات ====================
with tab2:
    col_add, col_file = st.columns([2, 1])
    
    with col_add:
        st.subheader(t["add_edit_prod"])
        edit_mode = st.checkbox(t["edit_mode_label"], value=False)
        
        selected_sku_to_edit = ""
        default_name, default_cat, default_init, default_price, default_min = "", "General", 0.0, 0.0, 5.0
        
        if edit_mode and not df_inv.empty:
            chosen_p = st.selectbox("---", df_inv['sku'] + " - " + df_inv['name'], label_visibility="collapsed")
            selected_sku_to_edit = chosen_p.split(" - ")[0]
            prod_row = df_inv[df_inv['sku'] == selected_sku_to_edit].iloc[0]
            default_name = prod_row['name']
            default_cat = prod_row['category']
            default_init = float(prod_row['initial_stock'])
            default_price = float(prod_row['price'])
            default_min = float(prod_row['min_limit'])

        with st.form("product_form"):
            p_sku = st.text_input(t["sku"], value=selected_sku_to_edit if edit_mode else "")
            p_name = st.text_input(t["name"], value=default_name)
            p_cat = st.selectbox(t["category"], ["General", "Electronics", "Parts", "Furniture"], index=0)
            p_init = st.number_input(t["initial_stock"], min_value=0.0, value=default_init, step=1.0)
            p_price = st.number_input(t["price"], min_value=0.0, value=default_price, step=0.5)
            p_min = st.number_input(t["min_limit"], min_value=0.0, value=default_min, step=1.0)
            
            btn_save = st.form_submit_button(t["btn_save_prod"])
            if btn_save and p_sku and p_name:
                c.execute('''INSERT INTO products (sku, name, category, initial_stock, price, min_limit)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ON CONFLICT(sku) DO UPDATE SET
                           name=excluded.name, category=excluded.category,
                           initial_stock=excluded.initial_stock,
                           price=excluded.price, min_limit=excluded.min_limit''',
                          (p_sku, p_name, p_cat, p_init, p_price, p_min))
                conn.commit()
                st.success(t["success_prod"])
                st.rerun()

    with col_file:
        st.subheader(t["import_excel"])
        up_file = st.file_uploader(t["file_uploader"], type=["xlsx", "csv"], label_visibility="collapsed")
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
                                     initial_stock=excluded.initial_stock,
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
            
            qty_out = col_s2.number_input(t["qty_sold"], min_value=1.0, value=1.0, step=1.0)
            client_name = col_s3.text_input(t["client_name"], value="General Client")
            
            st.info(f"{t['stock_available']}: {current_p['stock']} | {t['price']}: ${current_p['price']:,.2f}")
            
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
            
            qty_in = col_b2.number_input(t["qty_received"], min_value=1.0, value=1.0, step=1.0)
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
        
        history_excel = to_excel(df_history)
        st.download_button(
            label=t["download_history_excel"],
            data=history_excel,
            file_name="inventory_ledger_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info(t["no_history"])

# ==================== Tab 6: إعدادات الشركة ====================
with tab6:
    st.subheader(t["settings_title"])
    with st.form("settings_form"):
        s_name = st.text_input(t["comp_name"], value=get_setting("comp_name", ""))
        s_phone = st.text_input(t["comp_phone"], value=get_setting("comp_phone", ""))
        s_tax = st.text_input(t["comp_tax"], value=get_setting("comp_tax", ""))
        s_address = st.text_area(t["comp_address"], value=get_setting("comp_address", ""))
        
        btn_save_sets = st.form_submit_button(t["btn_save_settings"])
        if btn_save_sets:
            save_setting("comp_name", s_name)
            save_setting("comp_phone", s_phone)
            save_setting("comp_tax", s_tax)
            save_setting("comp_address", s_address)
            st.success(t["success_settings"])
            st.rerun()
