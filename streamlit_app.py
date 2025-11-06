# ---------------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ---------------------------------------------------------------

import os
from datetime import datetime
from io import BytesIO
import base64
import streamlit as st

# ===========================[ إعدادات عامة ]===========================
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# --------------------------[ أنماط واجهة ]-----------------------------
st.markdown("""
<style>
/* اجعل الهيدر مرناً كي لا يَقص الشعار */
[data-testid="stHeader"]{
  background: transparent !important;
  height: 48px !important;   /* يمكن رفعها إلى 56 إذا بقي جزء من الشعار مقصوص */
  box-shadow: none !important;
}
.block-container{
  padding-top: 28px !important;     /* مساحة علوية ليظهر الشعار + العنوان كاملاً */
}

/* عناوين الواجهة */
.ims-title{ font-size:48px; font-weight:900; line-height:1.1; margin:0 0 6px 0; color:#0f3b63;}
.ims-sub{ font-size:36px; font-weight:800; color:#b58500; margin:10px 0 6px 0; }
.ims-division{ font-size:22px; font-weight:700; color:#0f172a; margin:2px 0 18px 0; }

/* الشريط الذهبي */
.badge{
  background: linear-gradient(90deg, #c69b1b 0%, #a67c00 100%);
  color:#102a43; font-weight:800; border-radius:16px; padding:16px 22px; text-align:center;
  box-shadow: 0 2px 6px rgba(16,24,40,.10);
}

/* بطاقة إنجاز ISO (النص aa) */
.ims-ann-card{
  max-width: 980px; margin: 14px auto 24px auto; padding: 20px 22px;
  background:#ffffff; border:1px solid #e6edf3; border-radius:16px;
  box-shadow: 0 2px 6px rgba(16,24,40,.05);
  direction: rtl; text-align: justify; line-height: 2.05;
}
.ims-ann-title{
  margin: 0 auto 10px auto;
  text-align: center;
  font-size: 24px;
  font-weight: 800;
  color: #b58500;
  letter-spacing: .2px;
  border-bottom: 2px solid #e6c766;
  display: table;
  padding-bottom: 6px;
}
.ims-ann-body{ margin: 0; font-size: 17px; color:#0f172a }
.ims-iso{ color:#b58500; font-weight:800 }
.ims-bv{ font-weight:700 }

/* صناديق الواجهة */
.box{
  background:#eef5fb; border:1px solid #d7e6f5; color:#0f172a;
  padding:14px 16px; border-radius:12px;
}

/* لائحة الملفات */
.files-pill{
  display:inline-block; background:#f8fafc; border:1px solid #e5e7eb; color:#0f172a;
  padding:6px 10px; border-radius:10px; margin:4px 6px 0 0; font-size:13px;
}

/* حقل كلمة المرور */
.password-hint{ color:#64748b; font-size:13px; }

/* ترويسة العمود الأيسر */
.sidebar-title{ font-weight:800; color:#0f172a; }

/* توقيع */
.sig-wrap{
  margin:40px 0 6px 0; text-align:center; direction:rtl;
  color:#0f172a; font-weight:700;
}
.sig-wrap span{ color:#b58500; }
</style>
""", unsafe_allow_html=True)

# ===========================[ ثوابت ]===================================
MAX_MB = 200
MAX_BYTES = MAX_MB * 1024 * 1024
ALLOWED_EXT = {".pdf", ".docx", ".xlsx", ".xls", ".doc", ".pptx", ".ppt"}

# خريطة الأقسام (عربي -> (إنكليزي, slug, اسم السر))
SECTIONS_AR2EN = {
  "سياسة الجودة":            ("Quality Policy",         "policies",   "PW_POLICIES"),
  "الأهداف":                 ("Objectives",             "objectives", "PW_OBJECTIVES"),
  "ضبط الوثائق":            ("Document Control",       "docs",       "PW_DOCS"),
  "خطة التدقيق":            ("Audit Plan",             "audit_plan", "PW_AUDIT"),
  "نتائج التدقيق":           ("Audits",                 "audits",     "PW_AUDITS"),
  "عدم المطابقة":           ("Non-Conformance",        "nc",         "PW_NC"),
  "الإجراءات التصحيحية والوقائية (CAPA)": ("CAPA",   "capa",       "PW_CAPA"),
  "قاعدة المعرفة":          ("Knowledge Base",         "kb",         "PW_KB"),
  "التقارير":               ("Reports",                "reports",    "PW_REPORTS"),
  "مؤشرات الأداء (KPI)":    ("KPI",                    "kpi",        "PW_KPI"),
  "التوقيع الإلكتروني":     ("E-Sign",                 "esign",      "PW_ESIGN"),
  "الإشعارات":              ("Notify",                 "notify",     "PW_NOTIFY"),
  "المخاطر":                ("Risks",                  "risks",      "PW_RISKS"),
}

SECTIONS_AR = list(SECTIONS_AR2EN.keys())

# مجلد التخزين المحلي
BASE_DIR = os.path.join(".", "data")
os.makedirs(BASE_DIR, exist_ok=True)

def save_uploaded_file(buf: BytesIO, dest_path: str):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(buf.getbuffer())

def list_files(slug: str):
    d = os.path.join(BASE_DIR, slug)
    files = []
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            p = os.path.join(d, n)
            if os.path.isfile(p):
                files.append((n, os.path.getsize(p)))
    return files

def get_secret(secret_key: str) -> str:
    try:
        return st.secrets.get(secret_key, "")
    except Exception:
        return ""

# ===========================[ رأس الصفحة ]==============================
# شعار الشركة (أبقه بعرض مناسب حتى لا يُقص)
cols = st.columns([1, 4, 1])
with cols[0]:
    try:
        st.image("sold.png", width=120)
    except Exception:
        pass
with cols[1]:
    st.markdown(f"""
    <div style="text-align:center">
      <div class="ims-title">IMS — Integrated Management System</div>
      <div class="ims-sub">شركة نفط ذي قار</div>
      <div class="ims-division">شعبة الجودة وتقويم الأداء المؤسسي</div>
    </div>
    """, unsafe_allow_html=True)

# شريط الشهادة الذهبي
st.markdown(
    '<div class="badge">CERTIFIED ISO 9001:2015 — Bureau Veritas<br>'
    'Quality Management System — UKAS Accredited</div>',
    unsafe_allow_html=True
)

# نص الإنجاز (نسخة aa) أعلى الصفحة
aa_html = """
<div class="ims-ann-card">
  <h3 class="ims-ann-title">إنجاز وطني لشركة نفط ذي قار</h3>
  <p class="ims-ann-body">
    يُعَد حصول شركة نفط ذي قار على شهادة الاعتماد الدولي
    <span class="ims-iso">ISO 9001:2015</span>
    من مؤسسة <span class="ims-bv">Bureau Veritas</span> البريطانية إنجازًا وطنيًا واستراتيجيًا،
    تحقق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي في ترسيخ أنظمة الإدارة المتكاملة
    وتطبيق مفاهيم التحسين المستمر وتعزيز ثقافة الجودة في جميع تشكيلات الشركة،
    دعمًا لمسيرتها نحو التميز والشفافية والالتزام بأعلى المعايير العالمية.
  </p>
</div>
"""
st.markdown(aa_html, unsafe_allow_html=True)

# شهادة ISO (ثابتة في الواجهة إن رغبت)
try:
    st.image("iso_cert.jpg", use_column_width=True)
except Exception:
    pass

st.markdown("---")

# ===========================[ الشريط الجانبي ]==========================
st.sidebar.markdown('<div class="sidebar-title">اختر القسم</div>', unsafe_allow_html=True)
section_ar = st.sidebar.selectbox("اختر", SECTIONS_AR, index=0)
section_en, section_slug, secret_key = SECTIONS_AR2EN[section_ar]

# ===========================[ عرض الملفات الحالية ]=====================
st.subheader("الملفات الحالية (قراءة فقط)")
existing = list_files(section_slug)
if not existing:
    st.markdown(
        '<div class="box">لا توجد ملفات بعد في هذا القسم. استخدم لوحة التحكم لرفع الملفات بعد إدخال كلمة المرور الصحيحة.</div>',
        unsafe_allow_html=True
    )
else:
    for name, size in existing:
        st.markdown(f'<span class="files-pill">{name} — {round(size/1024,1)} KB</span>', unsafe_allow_html=True)

st.markdown("")

# ===========================[ لوحة التحكم / كلمة المرور ]================
st.subheader("لوحة التحكم (تتطلب كلمة مرور القسم)")
pwd_placeholder = f"مثال: {secret_key.lower().replace('pw_', '')}-2025" if secret_key else "••••••"
pwd_input = st.text_input("أدخل كلمة المرور", type="password", placeholder=pwd_placeholder)

true_pwd = get_secret(secret_key)
if not true_pwd:
    st.info("لم يتم ضبط كلمة مرور لهذا القسم في Secrets بعد.", icon="ℹ️")

if pwd_input:
    if pwd_input == true_pwd:
        st.success("تم التحقق من كلمة المرور. يمكنك رفع الملفات الآن.")
        # رافع الملفات
        uploads = st.file_uploader(
            f"ارفع ملفات قسم «{section_ar}» — حد {MAX_MB}MB للملف الواحد",
            type=[e.strip(".") for e in ALLOWED_EXT],
            accept_multiple_files=True
        )
        if uploads:
            for up in uploads:
                # تحقق الحجم والامتداد
                ext = os.path.splitext(up.name)[1].lower()
                if ext not in ALLOWED_EXT:
                    st.error(f"الملف {up.name}: امتداد غير مسموح.")
                    continue
                data = up.getvalue()
                if len(data) > MAX_BYTES:
                    st.error(f"الملف {up.name}: يتجاوز الحد {MAX_MB}MB.")
                    continue
                dest = os.path.join(BASE_DIR, section_slug, up.name)
                save_uploaded_file(BytesIO(data), dest)
            st.success("تم رفع الملفات بنجاح ✅")
            # تحديث العرض
            existing = list_files(section_slug)
            if existing:
                st.markdown("**الملفات بعد التحديث:**")
                for name, size in existing:
                    st.markdown(f'<span class="files-pill">{name} — {round(size/1024,1)} KB</span>', unsafe_allow_html=True)
    else:
        st.error("كلمة المرور غير صحيحة ❌")

# ===========================[ توقيع ]====================================
st.markdown("""
<hr style="margin:40px 0 12px 0; border:0; height:1px; background:#e6edf3;">
<div class="sig-wrap">
تصميم وتطوير رئيس مهندسين أقدم <span>طارق مجيد الكريمي</span>
</div>
""", unsafe_allow_html=True)

