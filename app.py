# 2. تنسيق شامل وإجبار كافة النصوص وخانات الرفع للظهور بوضوح تام
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

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

    /* إصلاح خانة رفع الملفات بالكامل */
    section[data-testid="stFileUploader"] {
        background-color: #1e293b !important;
        border: 2px dashed #3b82f6 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }

    section[data-testid="stFileUploader"] * {
        color: #ffffff !important;
        background-color: transparent !important;
    }

    section[data-testid="stFileUploader"] button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 6px 16px !important;
        font-weight: bold !important;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background-color: #0f172a !important;
        border-radius: 8px !important;
    }

    /* عناوين التبويبات (Tabs) */
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

    /* كافة النصوص والتسميات */
    label, p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    .stTextInput label p, .stNumberInput label p, .stSelectbox label p, .stFileUploader label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    /* حقول الإدخال */
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

    /* القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-left: 1px solid #334155;
    }

    /* بطاقات الإحصائيات KPIs */
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

    /* الأزرار العامة */
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
