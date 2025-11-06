# -*- coding: utf-8 -*-
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi

import os
import io
import base64
from datetime import datetime
import streamlit as st

# -------------------------------[ إعدادات عامة ]-------------------------------
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# مسار الحفظ الجذري للملفات
DATA_ROOT = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_ROOT, exist_ok=True)

MAX_MB = 200
MAX_BYTES = MAX_MB * 1024 * 1024
ACCEPT = ["pdf", "docx", "xlsx", "pptx"]

# ----------------------[ خريطة الأقسام عربي ⇄ إنجليزي ]-----------------------
SECTIONS_AR2EN = {
    "سياسة الجودة":               "quality-policy",
    "الأهداف":                   "objectives",
    "ضبط الوثائق":               "document-control",
    "خطة التدقيق":               "audit-plan",
    "نتائج التدقيق":             "audits",
    "عدم المطابقة":              "non-conformance",
    "الإجراءات التصحيحية والوقائية (CAPA)": "capa",
    "قاعدة المعرفة":             "knowledge-base",
    "التقارير":                  "reports",
    "مؤشرات الأداء (KPI)":       "kpi",
    "التوقيع الإلكتروني":        "e-sign",
    "الإشعارات":                 "notify",
    "المخاطر":                   "risks",           # جديد
}
SECTIONS_AR = list(SECTIONS_AR2EN.keys())

# ---------------------------[ كلمات المرور للأقسام ]---------------------------
# التزم بالصيَغ التي زوّدتني بها (+ قسم المخاطر):
PASSWORDS = {
    "quality-policy":  "policy-2025",
    "objectives":      "obj-2025",
    "document-control":"docs-2025",
    "audit-plan":      "audit-2025",
    "audits":          "audits-2025",
    "non-conformance": "nc-2025",
    "capa":            "capa-2025",
    "knowledge-base":  "kb-2025",
    "reports":         "reports-2025",
    "kpi":             "kpi-2025",
    "e-sign":          "esign-2025",
    "notify":          "notify-2025",
    "risks":           "risks-2025",
}

# -------------------------[ أدوات مساعدة ـ Utilities ]-------------------------
def normalize_pw(s: str) -> str:
    """تطبيع كلمة السر: إزالة محارف الاتجاه/المسافات وتوحيد الشرطة وتحويل الأرقام العربية إلى إنجليزية"""
    if not s:
        return ""
    s = s.strip()
    # إزالة محارف الاتجاه الشائعة
    for mark in ["\u200f", "\u200e", "\u202a", "\u202b", "\u2067", "\u2066"]:
        s = s.replace(mark, "")
    # توحيد الشرطة
    s = s.replace("–", "-").replace("—", "-").replace("ـ", "-")
    # تحويل الأرقام العربية إلى إنجليزية
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    for i, d in enumerate(arabic_digits):
        s = s.replace(d, str(i))
    return s

def ensure_section_dir(slug: str) -> str:
    path = os.path.join(DATA_ROOT, slug)
    os.makedirs(path, exist_ok=True)
    return path

def human_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} TB"

def list_files(slug: str):
    folder = ensure_section_dir(slug)
    files = []
    for name in sorted(os.listdir(folder)):
        fpath = os.path.join(folder, name)
        if os.path.isfile(fpath):
            files.append((name, os.path.getsize(fpath), fpath))
    return files

def file_download_link(name: str, fpath: str) -> str:
    # إنشاء رابط تنزيل (Data URI) لتجنّب المعاينة وفتح نافذة الحفظ مباشرة
    with open(fpath, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    ext = name.split(".")[-1].lower()
    mime = {
        "pdf":  "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }.get(ext, "application/octet-stream")
    href = f'<a href="data:{mime};base64,{b64}" download="{name}">⬇️ تنزيل</a>'
    return href

# -------------------------------[ تنسيق CSS ]-----------------------------------
st.markdown("""
<style>
  body, .stApp {background-color:#f5f7fb;}
  .ezrtsby0 {direction: rtl;}
  .block-container {padding-top: 2.2rem; padding-bottom: 2rem;}
  header {background: transparent;}
  /* عناوين الواجهة */
  .ims-title {font-size: 42px; font-weight: 800; color:#0e3a5d; text-align:center; line-height:1.25;}
  .ims-sub {font-size: 22px; font-weight: 700; color:#c58f06; text-align:center; margin-top: 14px;}
  .ims-dept {font-size: 20px; font-weight: 700; color:#112e51; text-align:center; margin: 4px 0 22px 0;}
  /* الشريط الذهبي */
  .ribbon {background: linear-gradient(90deg,#c79a0a,#a07100); color:#102235; 
           border-radius:14px; padding: 16px 22px; text-align:center; font-weight:800;}
  .badge-sub {display:block; font-weight:600; margin-top:6px;}
  /* بطاقة الإنجاز الوطني */
  .card {
    background:#ffffff; border:1px solid #e8edf3; border-radius:14px; 
    padding:18px 22px; box-shadow: 0 4px 10px rgba(16,35,53,0.06);
    margin-top:16px;
  }
  .card h4 {text-align:center; color:#b38307; font-weight:800; margin: 0 0 8px 0;}
  .card h4 span {border-bottom:3px solid #d5b15a; padding-bottom:3px;}
  .card p {margin:0; line-height:1.9; font-size:17px; color:#1c2e3a;}
  .card b {font-weight:800;}
  .gold {color:#b38307; font-weight:800;}
  /* رؤوس الأقسام */
  .sec-title {font-size:22px; font-weight:800; color:#102235; margin:14px 0 8px 0;}
  .hint {background:#e9f2ff; color:#1a3a5d; padding:10px 14px; border-radius:10px; font-size:14px;}
  .footer {text-align:center; margin-top:28px; color:#2d3a45;}
  .sig {color:#c58f06; font-weight:800;}
</style>
""", unsafe_allow_html=True)

# ------------------------------[ رأس الصفحة ]-----------------------------------
col_logo, col_title, _ = st.columns([1,3,1], vertical_alignment="center")
with col_logo:
    # ضع شعار الشركة في مجلد العمل باسم sold.png إن رغبت
    if os.path.exists("sold.png"):
        st.image("sold.png", width=120)
with col_title:
    st.markdown('<div class="ims-title">IMS — Integrated Management System</div>', unsafe_allow_html=True)
    st.markdown('<div class="ims-sub">شركة نفط ذي قار</div>', unsafe_allow_html=True)
    st.markdown('<div class="ims-dept">شعبة الجودة وتقويم الأداء المؤسسي</div>', unsafe_allow_html=True)

# شريط اعتماد الأيزو
st.markdown(
    '<div class="ribbon">CERTIFIED ISO 9001:2015 — Bureau Veritas'
    '<span class="badge-sub">Quality Management System — UKAS Accredited</span></div>',
    unsafe_allow_html=True
)

# بطاقة الإنجاز الوطني (المتنصف)
st.markdown(
    """
    <div class="card">
      <h4><span>إنجاز وطني لشركة نفط ذي قار</span></h4>
      <p>
      يُعَد حصول شركة نفط ذي قار على شهادة الاعتماد الدولي <span class="gold">ISO 9001:2015</span> من مؤسسة
      <b>Bureau Veritas</b> البريطانية إنجازًا وطنيًا واستراتيجيًا، تحقق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي
      في ترسيخ أنظمة الإدارة المتكاملة وتطبيق مفاهيم التحسين المستمر وتعزيز ثقافة الجودة في جميع تشكيلات الشركة،
      دعمًا لمسيرتها نحو <b>التميز</b> و<b>الشفافية</b> والالتزام بأعلى المعايير العالمية.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")  # فراغ بسيط

# -------------------------------[ اختيار القسم ]--------------------------------
st.sidebar.write("**اختر القسم**")
section_ar = st.sidebar.selectbox("اختر", SECTIONS_AR, index=0)
section_slug = SECTIONS_AR2EN[section_ar]
section_dir = ensure_section_dir(section_slug)

# ------------------------------[ عرض الملفات ]---------------------------------
st.markdown(f'<div class="sec-title">📂 الملفات الحالية (قراءة فقط)</div>', unsafe_allow_html=True)
files = list_files(section_slug)
if not files:
    st.markdown('<div class="hint">لا توجد ملفات بعد في هذا القسم. استخدم لوحة التحكم لرفع الملفات بعد إدخال كلمة المرور الصحيحة.</div>', unsafe_allow_html=True)
else:
    for name, size, path in files:
        col1, col2, col3 = st.columns([6,2,2])
        with col1:
            st.markdown(f"**{name}**")
        with col2:
            st.markdown(human_size(size))
        with col3:
            st.markdown(file_download_link(name, path), unsafe_allow_html=True)

st.write("")

# -----------------------------[ لوحة التحكم (محمية) ]--------------------------
st.markdown(f'<div class="sec-title">🔒 لوحة التحكم (تتطلب كلمة مرور القسم)</div>', unsafe_allow_html=True)
placeholder = {
    "quality-policy":"مثال: policy-2025", "objectives":"مثال: obj-2025", "document-control":"مثال: docs-2025",
    "audit-plan":"مثال: audit-2025", "audits":"مثال: audits-2025", "non-conformance":"مثال: nc-2025",
    "capa":"مثال: capa-2025", "knowledge-base":"مثال: kb-2025", "reports":"مثال: reports-2025",
    "kpi":"مثال: kpi-2025", "e-sign":"مثال: esign-2025", "notify":"مثال: notify-2025",
    "risks":"مثال: risks-2025",
}.get(section_slug, "أدخل كلمة المرور")

pw_raw = st.text_input("أدخل كلمة المرور", type="password", placeholder=placeholder)
pw = normalize_pw(pw_raw)

ok = (pw == PASSWORDS.get(section_slug))
if not ok:
    st.markdown('''<div class="hint">🔑 أدخل كلمة المرور الصحيحة لرفع الملفات إلى هذا القسم.</div>''', unsafe_allow_html=True)
else:
    # منطقة الرفع
    st.success("✅ تم التحقق من كلمة المرور. يمكنك رفع الملفات الآن.")
    up = st.file_uploader(
        f"ارفع ملف {section_ar} (حد أقصى {MAX_MB}MB لكل ملف) • الصيغ المسموحة: PDF, DOCX, XLSX, PPTX",
        type=ACCEPT, accept_multiple_files=True
    )
    if up:
        saved = 0
        for f in up:
            data = f.read()
            if len(data) > MAX_BYTES:
                st.error(f"❌ الملف **{f.name}** يتجاوز حد {MAX_MB}MB — لم يتم الحفظ.")
                continue
            # منع نفس الاسم: نضيف طابع وقت بسيط إن وجد تضارب
            dest = os.path.join(section_dir, f.name)
            if os.path.exists(dest):
                base, ext = os.path.splitext(f.name)
                dest = os.path.join(section_dir, f"{base}_{datetime.now().strftime('%Y%m%d-%H%M%S')}{ext}")
            with open(dest, "wb") as fh:
                fh.write(data)
            saved += 1
        if saved:
            st.success(f"👍 تم حفظ {saved} ملف/ملفات إلى قسم **{section_ar}**.")
            st.rerun()  # لإظهار القائمة المحدّثة مباشرة

# -------------------------------[ توقيع الفوتر ]--------------------------------
st.markdown(
    '<div class="footer">تصميم وتطوير رئيس مهندسين أقدم <span class="sig">طارق مجيد الكريمي</span> ©</div>',
    unsafe_allow_html=True
)
