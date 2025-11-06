# ------------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ------------------------------------------------------------

import os
import io
import hashlib
from datetime import datetime
from pathlib import Path

import streamlit as st

# =====================[ إعدادات عامة ]=====================
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# مسارات الصور المحلية
LOGO_PATH = "sold.png"        # ← شعار الشركة المحلي (تم تصحيح العرض من ملف محلي)
CERT_PATH = "iso_cert.jpg"    # ← صورة شهادة المنح (اختياري إن وُجدت)

# جذر التخزين داخل الحاوية
ROOT = Path("storage")
TRASH = ROOT / "_trash"
ROOT.mkdir(parents=True, exist_ok=True)
TRASH.mkdir(parents=True, exist_ok=True)

# خريطة الأقسام (عربي → Slug إنكليزي)
SECTIONS_AR2EN = {
    "سياسة الجودة":                 "Quality Policy",
    "الأهداف":                      "Objectives",
    "ضبط الوثائق":                  "Document Control",
    "خطة التدقيق":                  "Audit Plan",
    "نتائج التدقيق":                "Audits",
    "عدم المطابقة":                 "Non-Conformance",
    "الإجراءات التصحيحية والوقائية (CAPA)": "CAPA",
    "قاعدة المعرفة":                "Knowledge Base",
    "تقارير":                      "Reports",
    "مؤشرات الأداء (KPI)":          "KPI",
    "التوقيع الإلكتروني":           "E-Sign",
    "الإشعارات":                    "Notify",
    "المخاطر":                      "Risks",     # القسم الجديد
}
SECTIONS_AR = list(SECTIONS_AR2EN.keys())

# كلمات المرور من Secrets (اسماء المتغيرات كما زوّدتني بها)
PW = {
    "سياسة الجودة": st.secrets.get("PW_POLICIES",  "policy-2025"),
    "الأهداف":      st.secrets.get("PW_OBJECTIVES","obj-2025"),
    "ضبط الوثائق":  st.secrets.get("PW_DOCS",      "docs-2025"),
    "خطة التدقيق":  st.secrets.get("PW_AUDIT",     "audit-2025"),
    "نتائج التدقيق":st.secrets.get("PW_AUDITS",    "audits-2025"),
    "عدم المطابقة": st.secrets.get("PW_NC",        "nc-2025"),
    "الإجراءات التصحيحية والوقائية (CAPA)": st.secrets.get("PW_CAPA", "capa-2025"),
    "قاعدة المعرفة":st.secrets.get("PW_KB",        "kb-2025"),
    "تقارير":      st.secrets.get("PW_REPORTS",   "reports-2025"),
    "مؤشرات الأداء (KPI)": st.secrets.get("PW_KPI","kpi-2025"),
    "التوقيع الإلكتروني": st.secrets.get("PW_ESIGN","esign-2025"),
    "الإشعارات":    st.secrets.get("PW_NOTIFY",    "notify-2025"),
    "المخاطر":      st.secrets.get("PW_RISKS",     "risks-2025"),  # كلمة مرور للمخاطر
}

# =====================[ أدوات مساعدة ]=====================
def section_dir(ar_name: str) -> Path:
    slug = SECTIONS_AR2EN[ar_name]
    p = ROOT / slug
    p.mkdir(parents=True, exist_ok=True)
    return p

def file_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]

def safe_name(name: str) -> str:
    return "".join(c for c in name if c not in '\\/:*?"<>|').strip() or "file"

def save_unique(dirpath: Path, filename: str, data: bytes) -> Path:
    """يمنع التكرار عبر البصمة داخل القسم نفسه."""
    digest = file_sha256(data)
    stem = Path(filename).stem
    ext = Path(filename).suffix.lower() or ".bin"
    # لا نعيد رفع نفس البصمة
    for p in dirpath.glob(f"*{ext}"):
        if p.is_file():
            try:
                if file_sha256(p.read_bytes()) == digest:
                    return p  # ملف مطابق موجود مسبقاً
            except Exception:
                pass
    # اسم منسق مع ختم وقت
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    new_name = f"{safe_name(stem)}_{ts}_{digest}{ext}"
    dest = dirpath / new_name
    dest.write_bytes(data)
    return dest

def list_files(dirpath: Path):
    files = sorted([p for p in dirpath.glob("*") if p.is_file()], key=lambda p: p.name, reverse=True)
    return files

def move_to_trash(paths):
    TRASH.mkdir(parents=True, exist_ok=True)
    for p in paths:
        if p.exists():
            dest = TRASH / p.name
            # تجنب الكتابة فوق ملف بنفس الاسم داخل سلة المحذوفات
            if dest.exists():
                dest = TRASH / f"{p.stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}{p.suffix}"
            p.replace(dest)

# =====================[ تنسيقات CSS ]=====================
st.markdown("""
<style>
  .hero-wrap { text-align:center; margin: 8px 0 4px 0; }
  .ttl h1 { font-size: 44px; margin: 4px 0 2px 0; color:#0a3556; font-weight:900; }
  .ttl h2 { font-size: 32px; margin: 4px 0; color:#b8860b; font-weight:800;}
  .ttl h3 { font-size: 20px; margin: 0; color:#0b2e4d; font-weight:700; }
  .gold { background: linear-gradient(90deg,#caa019,#b07f0d);
          color:#122a3c; padding:14px 18px; border-radius:14px;
          font-weight:800; text-align:center; margin:12px auto; max-width: 900px; }
  .card { background:#ffffff; border:1px solid #e6eef7; border-radius:14px; padding:16px 18px;
          box-shadow: 0 2px 6px rgba(10,53,86,0.04); }
  .arab-center { text-align:center; direction: rtl; line-height:1.9; }
  .arab-justify { direction: rtl; text-align: justify; line-height:1.95; }
  .badge { display:inline-block; padding:4px 8px; border-radius:9px; background:#f0f6ff; color:#0a3556; font-size:12px; margin-left:6px; }
  .small { font-size:13px; color:#365; }
  .foot { text-align:center; color:#7a8b99; margin-top:18px; }
  .download-btn { text-align:left; }
</style>
""", unsafe_allow_html=True)

# =====================[ ترويسة الصفحة ]=====================
st.markdown("<div class='hero-wrap'>", unsafe_allow_html=True)
cols = st.columns([1, 3, 1])

with cols[0]:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
    else:
        st.write(" ")

with cols[1]:
    st.markdown("""
    <div class='ttl'>
      <h1>IMS — Integrated Management System</h1>
      <h2>شركة نفط ذي قار</h2>
      <h3>شعبة الجودة وتقويم الأداء المؤسسي</h3>
    </div>
    """, unsafe_allow_html=True)

with cols[2]:
    st.write(" ")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='gold'>CERTIFIED ISO 9001:2015 — Bureau Veritas — Quality Management System — UKAS Accredited</div>",
    unsafe_allow_html=True
)

# بطاقة الإنجاز الوطنية
st.markdown("""
<div class='card arab-center'>
  <h4 style="color:#b8860b; margin:0 0 6px 0;">إنجاز وطني لشركة نفط ذي قار</h4>
  <div class='arab-justify'>
    يُعَد حصول شركة نفط ذي قار على شهادة الاعتماد الدولي <b>ISO 9001:2015</b> من مؤسسة <b>Bureau Veritas</b> البريطانية إنجازًا وطنيًا واستراتيجيًا، تحقق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي في ترسيخ أنظمة الإدارة المتكاملة وتطبيق مفاهيم التحسين المستمر وتعزيز ثقافة الجودة في جميع تشكيلات الشركة، دعمًا لمسيرتها نحو التميز والشفافية والالتزام بأعلى المعايير العالمية.
  </div>
</div>
""", unsafe_allow_html=True)

# (اختياري) عرض مصغّر لشهادة المنح
if os.path.exists(CERT_PATH):
    st.image(CERT_PATH, caption="نسخة من شهادة المنح — Bureau Veritas — تموز 2025", use_container_width=True)

# =====================[ اختيار القسم ]=====================
st.sidebar.markdown("**اختر القسم**")
current_section = st.sidebar.selectbox("اختر", SECTIONS_AR, index=SECTIONS_AR.index("سياسة الجودة"))

# حالة المصادقة لكل قسم
if "auth" not in st.session_state:
    st.session_state.auth = {name: False for name in SECTIONS_AR}

sec_dir = section_dir(current_section)

# =====================[ عرض الملفات الحالية (روابط) ]=====================
st.markdown("### 🗂️ الملفات الحالية (قراءة فقط)  ")
files = list_files(sec_dir)

if not files:
    st.info("لا توجد ملفات بعد في هذا القسم. استخدم لوحة التحكم لرفع الملفات بعد إدخال كلمة المرور الصحيحة.")
else:
    for idx, p in enumerate(files, 1):
        fname = p.name
        with open(p, "rb") as f:
            data = f.read()
        col_t, col_d = st.columns([6, 1])
        with col_t:
            st.write(f"**#{idx} — {fname}**")
        with col_d:
            st.download_button("تنزيل", data=data, file_name=fname, key=f"dl-{current_section}-{idx}")

st.divider()

# =====================[ لوحة التحكم: كلمة مرور + دخول ]=====================
st.markdown("### 🔐 لوحة التحكم (تتطلب كلمة مرور القسم)")

with st.form("auth_form", clear_on_submit=False):
    pwd = st.text_input("أدخل كلمة المرور", type="password", placeholder=f"مثال: {PW[current_section]}")
    submitted = st.form_submit_button("دخول")
    if submitted:
        if pwd.strip() == PW[current_section]:
            st.session_state.auth[current_section] = True
            st.success("تمت المصادقة بنجاح. يمكنك الآن رفع/حذف الملفات لهذا القسم.")
        else:
            st.session_state.auth[current_section] = False
            st.error("كلمة المرور غير صحيحة.")

authed = st.session_state.auth[current_section]

# =====================[ لوحات الرفع والحذف ]=====================
if authed:
    st.markdown("### ⬆️ رفع ملف إلى هذا القسم")
    up_file = st.file_uploader("اختر ملفًا (PDF, DOCX, XLSX, PNG, JPG, ...)", type=None, accept_multiple_files=False)
    if up_file:
        data = up_file.read()
        dest = save_unique(sec_dir, up_file.name, data)
        st.success(f"تم الحفظ بنجاح: {dest.name}")

    st.markdown("### 🗑️ حذف جماعي (نقل إلى سلة المحذوفات)")
    selectable = [p.name for p in list_files(sec_dir)]
    if selectable:
        picks = st.multiselect("اختر الملفات:", options=selectable)
        col_del1, col_del2 = st.columns([1, 2])
        with col_del1:
            if st.button("نقل الملفات المختارة إلى سلة المحذوفات"):
                targets = [sec_dir / n for n in picks]
                move_to_trash(targets)
                st.success(f"تم نقل {len(targets)} ملف/ملفات إلى سلة المحذوفات.")
        with col_del2:
            st.caption("يمكن استرجاع الملفات لاحقًا من سلة المحذوفات يدويًا (داخل مجلد storage/_trash).")
else:
    st.info("أدخل كلمة المرور الصحيحة لتمكين التحكم بالملفات في هذا القسم.")

# =====================[ تذييل ]=====================
st.markdown(
    "<div class='foot'>تصميم وتطوير رئيس مهندسين أقدم <b>طارق مجيد الكريمي</b></div>",
    unsafe_allow_html=True
)
