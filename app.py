# 2. إضافة خلفية احترافية وتنسيق ألوان النصوص والتبويبات لضمان الوضوح
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* خلفية مستودع ولوجستيات */
    .stApp {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.95)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=1920&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        color: #f8fafc;
    }

    /* إصلاح لون عناوين التبويبات (Tabs) لتكون واضحة */
    button[data-baseweb="tab"] {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
    }

    /* إصلاح لون التسميات فوق حقول الإدخال (Labels) */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stFileUploader label {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }

    /* تحسين شكل حقول الإدخال */
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }

    /* تحسين القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.9) !important;
        border-left: 1px solid #334155;
    }

    /* تحسين تصميم بطاقات الأحصائيات KPIs */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid #334155 !important;
        border-right: 4px solid #3b82f6 !important;
        padding: 16px !important;
        border-radius: 12px !important;
        backdrop-filter: blur(8px);
    }

    div[data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-size: 0.95rem !important;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        font-size: 1.7rem !important;
    }

    /* إطارات الاستمارات */
    div[data-testid="stForm"], div.stTabs [data-baseweb="tab-panel"] {
        background: rgba(30, 41, 59, 0.85) !important;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(6px);
    }

    /* الأزرار */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
    }

    h1, h2, h3, h4 {
        color: #f1f5f9 !important;
        font-weight: 800 !important;
    }
    </style>
""", unsafe_allow_html=True)
