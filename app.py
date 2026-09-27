# تطبيق تصميم وقالب احترافي (Modern Dashboard UI)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    /* 1. التنسيق العام والخطوط */
    html, body, [class*="css"], .stApp {{
        font-family: {t['font']} !important;
        direction: {t['dir']};
        background-color: #0f172a; /* خلفية داكنة احترافية Slate 900 */
        color: #f8fafc;
    }}

    /* 2. تحسين القائمة الجانبية */
    section[data-testid="stSidebar"] {{
        background-color: #1e293b !important; /* Slate 800 */
        border-{"left" if t['dir']=='rtl' else "right"}: 1px solid #334155;
    }}

    /* 3. تصميم تبويبات التنقل العلوية (Tabs) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: #1e293b;
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid #334155;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 45px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #94a3b8 !important;
        font-weight: 600;
        border: none !important;
        padding: 0 16px;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #2563eb !important; /* أزرق احترافي Primary */
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }}

    /* 4. بطاقات المؤشرات (KPI Cards) */
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155 !important;
        border-{"right" if t['dir']=='rtl' else "left"}: 4px solid #2563eb !important;
        padding: 18px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(37, 99, 235, 0.2);
    }}

    div[data-testid="stMetricLabel"] {{
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
        font-weight: 500;
    }}

    div[data-testid="stMetricValue"] {{
        color: #f8fafc !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }}

    /* 5. تحسين الأزرار (Buttons) */
    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.6) !important;
    }}

    /* 6. تحسين حقول الإدخال والجداول */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{
        background-color: #1e293b !important;
        border-color: #334155 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
    }}

    div[data-testid="stForm"] {{
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
    }}
    </style>
""", unsafe_allow_html=True)
