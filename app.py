/* إصلاح شامل ودقيق لخانة رفع الملفات */
    div[data-testid="stFileUploader"] {
        background-color: #0f172a !important;
        border: 2px dashed #3b82f6 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }

    div[data-testid="stFileUploader"] section {
        background-color: #0f172a !important;
    }

    /* تغيير لون الزر الداخلي (Browse files) إلى الأزرق بالنص الأبيض */
    div[data-testid="stFileUploader"] button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 8px 18px !important;
        font-weight: bold !important;
        box-shadow: none !important;
    }

    div[data-testid="stFileUploader"] button * {
        color: #ffffff !important;
    }

    /* نص التعليمات الجانبي (Limit 200MB per file...) */
    div[data-testid="stFileUploader"] small, 
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] p {
        color: #cbd5e1 !important;
    }
