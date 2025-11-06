# --------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# --------------------------------------------------------

import os
from datetime import datetime
from io import BytesIO
import base64
import streamlit as st

# =========================[ إعدادات عامة ]=========================
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# ألوان وخلفية خفيفة
st.markdown("""
<style>
    body, .stApp {background-color:#f3f7fc;}
    .block-container {padding-top:1.5rem; padding-bottom:1.5rem;}
    .stSelectbox [data-baseweb="select"] {direction: rtl;}
</style>
""", unsafe_allow_html=True)

# دالة مساعده للوصول للملفات المرفقة (محلية داخل مجلد مؤقت للتطبيق)
def safe_filename(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum() or ch in (" ", ".", "-", "_")).strip()

# ===================[ ترويسة: الشعار + العناوين ]==================
col_logo, col_title, col_empty = st.columns([1, 3, 1])

with col_logo:
    logo_path = os.path.join(os.path.dirname(__file__), "sold.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

with col_title:
    st.markdown(
        """
        <div style='text-align:center; line-height:1.8; margin-top:-10px;'>
            <h1 style='color:#0a3d62; font-size:44px; font-weight:800; margin:0 0 6px 0;'>
                IMS — Integrated Management System
            </h1>
            <h2 style='color:#b8860b; font-size:36px; font-weight:800; margin:0 0 4px 0;'>
                شركة نفط ذي قار
            </h2>
            <h3 style='color:#2c3e50; font-size:26px; margin:4px 0 8px 0;'>
                شعبة الجودة وتقويم الأداء المؤسسي
            </h3>
            <p style='font-size:18px; color:#1e272e; font-weight:500; margin:10px auto 0; max-width:980px;'>
                يُعَد حصول <strong>شركة نفط ذي قار</strong> على شهادة الاعتماد الدولي
                <strong>ISO</strong> إنجازًا وطنيًا واستراتيجيًا تحقق بفضل الجهود
                المتميزة التي بذلتها <strong>شعبة الجودة وتقويم الأداء المؤسسي</strong>
                في ترسيخ أنظمة الإدارة المتكاملة وتطبيق مفاهيم التحسين المستمر
                وتعزيز ثقافة الجودة في جميع أقسام الشركة. هذا الإنجاز يجسّد التزام
                الشركة بالتميّز والشفافية والامتثال لأعلى المعايير العالمية.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================[ شهادة ISO (صورة ثابتة) ]=====================
iso_img = os.path.join(os.path.dirname(__file__), "iso_cert.jpg")
if os.path.exists(iso_img):
    st.markdown(
        """
        <div style='text-align:center; margin:18px auto 8px;'>
            <h4 style='color:#0a3d62; margin:0 0 8px 0;'>نسخة من شهادة الاعتماد الدولي ISO 9001:2015</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.image(iso_img, width=640, caption="شهادة الاعتماد الممنوحة لشركة نفط ذي قار من شركة Bureau Veritas — 21 تموز 2025")

# =======================[ ثوابت وخرائط الأقسام ]======================
MAX_MB = 200
MAX_BYTES = MAX_MB * 1024 * 1024

SECTIONS_AR2EN = {
    "سياسة الجودة": "Quality Policy",
    "الأهداف": "Objectives",
    "ضبط الوثائق": "Document Control",
    "خطة التدقيق": "Audit Plan",
    "نتائج التدقيق": "Audits",
    "عدم المطابقة": "Non-Conformance",
    "الإجراءات التصحيحية والوقائية (CAPA)": "CAPA",
    "قاعدة المعرفة": "Knowledge Base",
    "التقارير": "Reports",
    "مؤشرات الأداء (KPI)": "KPI",
    "التواقيع الإلكترونية": "E-Sign",
    "الإشعارات": "Notify",
    "المخاطر": "Risks"
}
SECTIONS_AR = list(SECTIONS_AR2EN.keys())

# كلمات المرور من Secrets مع قيم افتراضية للأمان أثناء الاختبار
def sec(key, default=""):
    try:
        return st.secrets[key]
    except Exception:
        return default

PASSWORDS = {
    "Quality Policy":   sec("PW_POLICIES",  "policy-2025"),
    "Objectives":       sec("PW_OBJECTIVES","obj-2025"),
    "Document Control": sec("PW_DOCS",      "docs-2025"),
    "Audit Plan":       sec("PW_AUDIT",     "audit-2025"),
    "Audits":           sec("PW_AUDITS",    "audits-2025"),
    "Non-Conformance":  sec("PW_NC",        "nc-2025"),
    "CAPA":             sec("PW_CAPA",      "capa-2025"),
    "Knowledge Base":   sec("PW_KB",        "kb-2025"),
    "Reports":          sec("PW_REPORTS",   "reports-2025"),
    "KPI":              sec("PW_KPI",       "kpi-2025"),
    "E-Sign":           sec("PW_ESIGN",     "esign-2025"),
    "Notify":           sec("PW_NOTIFY",    "notify-2025"),
    "Risks":            sec("PW_RISKS",     "risks-2025"),
}

# أمثلة للمكان المخصص Placeholders حسب القسم
PLACEHOLDERS = {
    "Quality Policy": "policy-2025", "Objectives": "obj-2025",
    "Document Control": "docs-2025", "Audit Plan": "audit-2025",
    "Audits": "audits-2025", "Non-Conformance": "nc-2025",
    "CAPA": "capa-2025", "Knowledge Base": "kb-2025",
    "Reports": "reports-2025", "KPI": "kpi-2025",
    "E-Sign": "esign-2025", "Notify": "notify-2025",
    "Risks": "risks-2025"
}

# ================ [ الشريط الجانبي: اختيار القسم ] ================
st.sidebar.markdown("<h4 style='text-align:right;'>اختر القسم</h4>", unsafe_allow_html=True)
selected_ar = st.sidebar.selectbox("اختر القسم", SECTIONS_AR, index=0)
section_key = SECTIONS_AR2EN[selected_ar]

# ===============[ عرض الملفات الحالية (قراءة فقط) ]================
st.markdown("### 📂 الملفات الحالية (قراءة فقط)")
st.info("لا توجد ملفات بعد في هذا القسم. جرّب لوحة التحكم لرفع الملفات بعد إدخال كلمة المرور الصحيحة.")

# ======================[ لوحة التحكم والباسوورد ]=====================
st.markdown("### 🔐 لوحة التحكم (تتطلب كلمة مرور القسم)")
pw_label = f"أدخل كلمة المرور لقسم «{selected_ar}»"
entered_pw = st.text_input(pw_label, type="password",
                           placeholder=f"مثال: {PLACEHOLDERS.get(section_key,'policy-2025')}")

if entered_pw:
    if entered_pw == PASSWORDS.get(section_key, ""):
        st.success("تم التحقق بنجاح — يمكنك رفع الملفات الآن.")
        st.caption(f"حد الرفع: {MAX_MB}MB لكل ملف. الصيغ: PDF, DOCX, XLSX")

        files = st.file_uploader("ارفع الملفات هنا", type=["pdf", "docx", "xlsx"],
                                 accept_multiple_files=True)
        if files:
            saved = 0
            save_root = os.path.join(os.path.dirname(__file__), "uploaded", section_key)
            os.makedirs(save_root, exist_ok=True)

            for f in files:
                if f.size > MAX_BYTES:
                    st.error(f"❌ {f.name} يتجاوز {MAX_MB}MB — لم يتم حفظه.")
                    continue
                fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_filename(f.name)}"
                with open(os.path.join(save_root, fname), "wb") as out:
                    out.write(f.read())
                saved += 1

            if saved:
                st.success(f"✅ تم حفظ {saved} ملف(ات) بنجاح داخل مجلد: uploaded/{section_key}")
                st.caption("تنبيه: التخزين داخل بيئة الاستضافة مؤقت وقد يُعاد ضبطه. للحفظ الدائم استخدم Google Drive أو S3 في خطوة لاحقة.")
    else:
        st.error("كلمة المرور غير صحيحة. يرجى التحقق من قائمة كلمات المرور.")

# ===============================[ تذييل ]=============================
st.markdown(
    """
    <hr style='margin:28px 0 10px 0;'>
    <p style='text-align:center; color:#6b7280; font-size:14px;'>
        تصميم وتطوير رئيس مهندسين أقدم <strong>طارق مجيد الكريمي</strong> — شركة نفط ذي قار
    </p>
    """,
    unsafe_allow_html=True
)
