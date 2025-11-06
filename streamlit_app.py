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

# ------------------------------[ إعداد عام ]------------------------------
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# ثابتات الحجم والأنواع
MAX_MB = 200
MAX_BYTES = MAX_MB * 1024 * 1024
ACCEPT = ["pdf", "docx", "xlsx", "pptx"]

# مجلد تخزين محلي لكل قسم
BASE_DIR = "data"
os.makedirs(BASE_DIR, exist_ok=True)

# ---------------------------[ تنسيقات CSS ]---------------------------
st.markdown("""
<style>
  :root { --brand:#0a3d62; --gold:#c9a227; --gold2:#9f7d12; }
  .stApp { background: #eef4fb; }
  /* رأس */
  .hero { text-align:center; padding: 12px 0 4px 0; }
  .hero h1 { color:#0a3d62; font-size: 46px; line-height:1.2; margin: 0 0 4px; font-weight:800; }
  .hero h2 { color:#c09200; font-size: 38px; margin: 6px 0 0 0; font-weight:800; }
  .hero h3 { color:#0a3d62; font-size: 22px; margin-top: 6px; font-weight:800; letter-spacing:.2px; }
  .subnote { text-align:center; font-size:13px; color:#2d3436; margin-top:4px }
  /* شريط الشهادة */
  .iso-banner { background: linear-gradient(90deg, var(--gold), var(--gold2));
                color:#0b1320; border-radius: 14px; padding: 14px 18px; 
                font-weight:800; text-align:center; margin: 10px 0 14px 0; }
  .iso-sub { font-size:14px; color:#0b1320; margin-top:4px; }
  /* بطاقة الإنجاز */
  .award { background:#fff; border-radius:14px; padding:18px 22px; 
           border: 1px solid #e6e6e6; box-shadow:0 2px 10px rgba(0,0,0,.04); }
  .award h4 { color:#c09200; text-align:center; margin:0 0 8px 0; 
              font-weight:800; font-size:22px; border-bottom:2px solid #e6d18f;
              display:inline-block; padding:0 10px 6px; }
  .award p { margin:10px 0 0 0; line-height:2.0; font-size:15.8px; color:#222; text-align:justify; }
  .award .em { font-weight:800; }
  .sec-title { font-size:22px; font-weight:800; color:#14213d; margin: 8px 0 10px; }
  .hint { background:#eef5ff; border:1px dashed #9bb9ff; padding:10px 12px; 
          border-radius:10px; color:#0b2b66; font-size:13px; }
  .files-box { background:#f8fbff; border:1px solid #eef1f5; border-radius:12px; padding:10px 14px; }
  .file-row { display:flex; align-items:center; justify-content:space-between; 
              padding:6px 8px; border-bottom:1px dashed #e5ecf7; }
  .file-row:last-child { border-bottom:none; }
  .file-name { font-size:14.5px; color:#0b2b66; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .footer { text-align:center; font-size:13px; color:#444; margin-top:26px; }
  .sig { color:#b7791f; font-weight:800; }
  /* تصغير شعار الشركة عند الرأس */
  .toc-logo { width: 120px; }
</style>
""", unsafe_allow_html=True)

# -------------------------[ أدوات مساعدة ]-------------------------
def normalize_pw(s: str) -> str:
    """تطبيع كلمة المرور: إزالة الفراغات وتحويل الأرقام العربية إلى إنجليزية وخفض الحروف."""
    if not s:
        return ""
    s = s.strip()
    # أرقام عربية -> إنجليزية
    trans = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    s = s.translate(trans)
    return s.lower()

def section_dir_for(slug: str) -> str:
    d = os.path.join(BASE_DIR, slug)
    os.makedirs(d, exist_ok=True)
    return d

def files_of(slug: str):
    d = section_dir_for(slug)
    files = []
    for name in os.listdir(d):
        p = os.path.join(d, name)
        if os.path.isfile(p):
            files.append((name, os.path.getmtime(p), p))
    # ترتيب الأحدث أولاً
    files.sort(key=lambda t: t[1], reverse=True)
    return files

def download_link(label: str, path: str, key: str):
    with open(path, "rb") as f:
        data = f.read()
    st.download_button(
        label=label,
        data=data,
        file_name=os.path.basename(path),
        mime="application/octet-stream",
        key=key,
        use_container_width=False
    )

# ---------------------------[ الأقسام ]---------------------------
SECTIONS_AR2EN = {
    "سياسة الجودة": "quality-policy",
    "الأهداف": "objectives",
    "ضبط الوثائق": "document-control",
    "خطة التدقيق": "audit-plan",
    "نتائج التدقيق": "audits",
    "عدم المطابقة": "non-conformance",
    "الإجراءات التصحيحية والوقائية (CAPA)": "capa",
    "قاعدة المعرفة": "knowledge-base",
    "التقارير": "reports",
    "مؤشرات الأداء (KPI)": "kpi",
    "التوقيع الإلكتروني": "e-sign",
    "الإشعارات": "notify",
    "المخاطر": "risks",  # جديد
}
SECTIONS_AR = list(SECTIONS_AR2EN.keys())

# ربط أسماء الأسرار مع الأقسام
SECT2SECRET = {
    "quality-policy": "PW_POLICIES",
    "objectives": "PW_OBJECTIVES",
    "document-control": "PW_DOCS",
    "audit-plan": "PW_AUDIT",
    "audits": "PW_AUDITS",
    "non-conformance": "PW_NC",
    "capa": "PW_CAPA",
    "knowledge-base": "PW_KB",
    "reports": "PW_REPORTS",
    "kpi": "PW_KPI",
    "e-sign": "PW_ESIGN",
    "notify": "PW_NOTIFY",
    "risks": "PW_RISKS",
}

# قراءة كلمات المرور من Secrets
PASSWORDS = {}
for slug, secret_name in SECT2SECRET.items():
    PASSWORDS[slug] = normalize_pw(st.secrets.get(secret_name, ""))

# ---------------------------[ رأس الصفحة ]---------------------------
logo_path = "sold.png"  # تأكد أن اسم الملف صحيح داخل المستودع
colL, colC, colR = st.columns([1,3,1])
with colL:
    if os.path.exists(logo_path):
        st.image(logo_path, caption="", width=120)
with colC:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<h1>IMS — Integrated Management System</h1>', unsafe_allow_html=True)
    st.markdown('<h2>شركة نفط ذي قار</h2>', unsafe_allow_html=True)
    st.markdown('<h3>شعبة الجودة وتقويم الأداء المؤسسي</h3>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="iso-banner">CERTIFIED ISO 9001:2015 — Bureau Veritas'
            '<div class="iso-sub">Quality Management System — UKAS Accredited</div>'
            '</div>', unsafe_allow_html=True)

# بطاقة الإنجاز الوطني
st.markdown(
    """
    <div class="award">
      <h4>إنجاز وطني لشركة نفط ذي قار</h4>
      <p>
      يُعَد حصول شركة نفط ذي قار على شهادة الاعتماد الدولي <span class="em">ISO 9001:2015</span>
      من مؤسسة <span class="em">Bureau Veritas</span> البريطانية إنجازًا وطنيًا واستراتيجيًا،
      تحقّق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي في ترسيخ أنظمة الإدارة المتكاملة
      وتطبيق مفاهيم التحسين المستمر وتعزيز ثقافة الجودة في جميع تشكيلات الشركة، دعمًا لمسيرتها
      نحو التميّز والشفافية، والالتزام بأعلى المعايير العالمية.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ----------------------------[ اختيار القسم ]----------------------------
st.sidebar.subheader("اختر القسم")
section_ar = st.sidebar.selectbox("اختر", SECTIONS_AR, index=0)
section_slug = SECTIONS_AR2EN[section_ar]
section_dir = section_dir_for(section_slug)

# -----------------------[ الملفات الحالية (قراءة فقط) ]-----------------------
st.markdown(f'<div class="sec-title">📁 الملفات الحالية (قراءة فقط)</div>', unsafe_allow_html=True)
all_files = files_of(section_slug)

if not all_files:
    st.info("لا توجد ملفات بعد في هذا القسم. استخدم لوحة التحكم لرفع الملفات بعد إدخال كلمة المرور الصحيحة.")
else:
    with st.container(border=True):
        for i, (name, mtime, path) in enumerate(all_files, start=1):
            c1, c2 = st.columns([5,1])
            with c1:
                st.markdown(f'<div class="file-row"><div class="file-name">#{i} — {name}</div></div>', unsafe_allow_html=True)
            with c2:
                download_link("تنزيل", path, key=f"dl-{section_slug}-{i}")

# -----------------------------[ لوحة التحكم (محمية) ]--------------------------
st.markdown(f'<div class="sec-title">🔒 لوحة التحكم (تتطلب كلمة مرور القسم)</div>', unsafe_allow_html=True)

placeholder = {
    "quality-policy":"مثال: policy-2025", "objectives":"مثال: obj-2025", "document-control":"مثال: docs-2025",
    "audit-plan":"مثال: audit-2025", "audits":"مثال: audits-2025", "non-conformance":"مثال: nc-2025",
    "capa":"مثال: capa-2025", "knowledge-base":"مثال: kb-2025", "reports":"مثال: reports-2025",
    "kpi":"مثال: kpi-2025", "e-sign":"مثال: esign-2025", "notify":"مثال: notify-2025",
    "risks":"مثال: risks-2025",
}.get(section_slug, "أدخل كلمة المرور")

auth_key = f"auth_{section_slug}"
if auth_key not in st.session_state:
    st.session_state[auth_key] = False

with st.form(f"pw_form_{section_slug}", clear_on_submit=False):
    pw_raw = st.text_input("أدخل كلمة المرور", type="password", placeholder=placeholder)
    submitted = st.form_submit_button("دخول")

if submitted:
    pw = normalize_pw(pw_raw)
    st.session_state[auth_key] = (pw == PASSWORDS.get(section_slug))
    if not st.session_state[auth_key]:
        st.error("❌ كلمة المرور غير صحيحة.")

if st.session_state[auth_key]:
    st.success("✅ تم التحقق من كلمة المرور. يمكنك رفع الملفات الآن.")
    if st.button("تسجيل خروج", type="secondary"):
        st.session_state[auth_key] = False
        st.rerun()

if st.session_state[auth_key]:
    uploads = st.file_uploader(
        f"ارفع ملف {section_ar} (حد أقصى {MAX_MB}MB لكل ملف) • الصيغ: PDF, DOCX, XLSX, PPTX",
        type=ACCEPT, accept_multiple_files=True
    )
    if uploads:
        saved = 0
        for f in uploads:
            data = f.read()
            if len(data) > MAX_BYTES:
                st.error(f"❌ الملف **{f.name}** يتجاوز حد {MAX_MB}MB — لم يتم الحفظ.")
                continue
            dest = os.path.join(section_dir, f.name)
            if os.path.exists(dest):
                base, ext = os.path.splitext(f.name)
                dest = os.path.join(section_dir, f"{base}_{datetime.now().strftime('%Y%m%d-%H%M%S')}{ext}")
            with open(dest, "wb") as fh:
                fh.write(data)
            saved += 1
        if saved:
            st.success(f"👍 تم حفظ {saved} ملف/ملفات إلى قسم **{section_ar}**.")
            st.rerun()
else:
    st.markdown('<div class="hint">🔑 أدخل كلمة المرور ثم اضغط «دخول» لتمكين رفع الملفات.</div>', unsafe_allow_html=True)

# -------------------------------[ تذييل ]-------------------------------
st.markdown(
    '<div class="footer">تصميم وتطوير <span class="sig">رئيس مهندسين أقدم طارق مجيد الكريمي</span> ©</div>',
    unsafe_allow_html=True
)
