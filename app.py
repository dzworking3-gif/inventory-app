with col_file:
        st.subheader("📥 استيراد من Excel")
        up_file = st.file_uploader("رفع ملف Excel", type=["xlsx", "csv"])
        if up_file:
            try:
                df_up = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
                
                # توحيد أسماء الأعمدة لتفادي أخطاء اختلاف المسميات
                column_mapping = {
                    'رقم المنتج (SKU)': 'SKU', 'رقم المنتج': 'SKU', 'sku': 'SKU',
                    'اسم المنتج': 'Name', 'الاسم': 'Name', 'name': 'Name',
                    'الفئة': 'Category', 'category': 'Category',
                    'المخزون الأول': 'InitialStock', 'المخزون الأولي': 'InitialStock', 'initialstock': 'InitialStock', 'stock': 'InitialStock',
                    'سعر الوحدة': 'Price', 'السعر': 'Price', 'price': 'Price',
                    'حد الطلب الأدنى': 'MinLimit', 'حد الطلب': 'MinLimit', 'minlimit': 'MinLimit'
                }
                
                # تنظيف أسماء الأعمدة وتطبيق الخريطة
                df_up.columns = [str(col).strip() for col in df_up.columns]
                df_up.rename(columns=column_mapping, inplace=True)
                
                # التأكد من وجود العناوين الأساسية أو تعيين قيم افتراضية
                for _, row in df_up.iterrows():
                    sku_val = str(row.get('SKU', ''))
                    name_val = str(row.get('Name', 'منتج جديد'))
                    cat_val = str(row.get('Category', 'عام'))
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
                st.success("تم استيراد البيانات بنجاح!")
                st.rerun()
            except Exception as e:
                st.error(f"خطأ أثناء التحميل: {e}")
