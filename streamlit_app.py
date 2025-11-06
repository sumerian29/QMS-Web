# --------------------------------------------------------------
# IMS — Thi Qar Oil Company (Arabic UI) • Streamlit
# تصميم وتطوير رئيس مهندسين أقدم طارق مجيد الكريمي
# --------------------------------------------------------------

import os
import io
import hashlib
from datetime import datetime
from typing import List, Tuple

import streamlit as st

# ========================= إعدادات عامة =========================
APP_TITLE = "IMS — Thi Qar Oil Company"
BASE_DIR = "uploads"              # مجلد حفظ الملفات
MAX_MB = 200                      # حد الحجم لكل ملف
MAX_BYTES = MAX_MB * 1024 * 1024

# صيغ مسموحة (تنزيل فقط، بدون معاينة تلقائية)
ACCEPT = ["pdf", "docx", "xlsx", "pptx"]

# أقسام النظام (عربي ← مفتاح إنجليزي)
SECTIONS_AR2EN = {
    "سياسة الجودة": "policies",
    "الأهداف": "objectives",
    "ضبط الوثائق": "document-control",
    "خطة التدقيق": "audit-plan",
    "نتائج التدقيق": "audits",
    "عدم المطابقة": "nc",
    "الإجراءات التصحيحية والوقائية (CAPA)": "capa",
    "قاعدة المعرفة": "kb",
    "التقارير": "reports",
    "مؤشرات الأداء (KPI)": "kpi",
    "التوقيع الإلكتروني": "esign",
    "التنبيهات": "notify",
    "المخاطر": "risks",  # القسم الجديد
}

# مفاتيح كلمات المرور (تُقرأ من Secrets)
PW_KEYS = {
    "policies": "PW_POLICIES",
    "objectives": "PW_OBJECTIVES",
    "document-control": "PW_DOCS",
    "audit-plan": "PW_AUDIT",
    "audits": "PW_AUDITS",
    "nc": "PW_NC",
    "capa": "PW_CAPA",
    "kb": "PW_KB",
    "reports": "PW_REPORTS",
    "kpi": "PW_KPI",
    "esign": "PW_ESIGN",
    "notify": "PW_NOTIFY",
    "risks": "PW_RISKS",  # مضاف
}

# ========================= أدوات مساعدة =========================
def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def human_size(num_bytes: int) -> str:
    for unit in ["B","KB","MB","GB","TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"

def file_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def list_files(section_slug: str) -> List[Tuple[str, int, str]]:
    """
    يعيد قائمة (اسم, حجم, مسار) مرتبة بالزمن تنازليًا.
    """
    section_dir = os.path.join(BASE_DIR, section_slug)
    if not os.path.isdir(section_dir):
        return []
    rows = []
    for name in os.listdir(section_dir):
        p = os.path.join(section_dir, name)
        if os.path.isfile(p):
            try:
                size = os.path.getsize(p)
                rows.append((name, size, p))
            except OSError:
                pass
    # الأحدث أولاً
    rows.sort(key=lambda r: os.path.getmtime(r[2]), reverse=True)
    return rows

def read_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets[key]
    except Exception:
        return default

def auth_state_key(section_slug: str) -> str:
    return f"auth_{section_slug}"

def uploader_key(section_slug: str) -> str:
    return f"uploader_{section_slug}"

# ========================= تهيئة الصفحة =========================
st.set_page_config(page_title=APP_TITLE, layout="wide")

# تنسيق بسيط
st.markdown("""
<style>
body, .stApp { background-color: #f1f6fb; }
.block-container { padding-top: 1.2rem; }
h1, h2, h3 { font-family: 'Segoe UI', Tahoma, sans-serif; }
.gold { color:#C29400; font-weight:700; }
.card {
  background: #ffffff; border: 1px solid #e8eef6; border-radius: 14px;
  padding: 16px 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.05);
}
.badge {
  display:inline-block; padding:10px 18px; border-radius:14px;
  background: linear-gradient(90deg,#caa21d,#a87a00); color:#0c2a3e; font-weight:800;
}
.code-note { color:#4d6e87; font-size:.92rem; }
.footer { text-align:center; color:#8aa1b3; padding:28px 0 10px; }
</style>
""", unsafe_allow_html=True)

colL, colC, colR = st.columns([1.2, 2.3, 1])

with colC:
    st.markdown(f"<h1 style='text-align:center;margin:0 0 6px'>{APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='gold' style='text-align:center;margin:6px 0'>شركة نفط ذي قار</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;margin-top:-6px'>شعبة الجودة وتقويم الأداء المؤسسي</h4>", unsafe_allow_html=True)
    st.markdown("<div class='badge' style='text-align:center;margin:18px auto'>CERTIFIED ISO 9001:2015 — Bureau Veritas<br>Quality Management System — UKAS Accredited</div>", unsafe_allow_html=True)

# بطاقة الإنجاز (ثابتة أعلى الصفحة)
with st.container():
    st.markdown(
        """
<div class='card' style='max-width:1100px;margin: 10px auto'>
  <h4 class='gold' style='text-align:center;margin-top:2px'>إنجازٌ وطنيٌ لشركة نفط ذي قار</h4>
  <p style='direction:rtl; text-align:justify; line-height:2'>
    يُعَد حصول شركة نفط ذي قار على شهادة الاعتماد الدولي <b style="color:#b8860b">ISO 9001:2015</b>
    من مؤسسة <b>Bureau Veritas</b> البريطانية إنجازًا وطنيًا واستراتيجيًا،
    تحقق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي في ترسيخ أنظمة الإدارة المتكاملة
    وتطبيق مفاهيم التحسين المستمر وتعزيز ثقافة الجودة في جميع تشكيلات الشركة،
    دعمًا لمسيرتها نحو التميز والشفافية، والالتزام بأعلى المعايير العالمية.
  </p>
</div>
        """,
        unsafe_allow_html=True,
    )

# ========================= اختيار القسم =========================
st.sidebar.header("اختر القسم")
section_ar = st.sidebar.selectbox("اختر", list(SECTIONS_AR2EN.keys()))
section_slug = SECTIONS_AR2EN[section_ar]
section_dir = os.path.join(BASE_DIR, section_slug)
ensure_dir(section_dir)

# حالة الدخول للقسم
auth_key = auth_state_key(section_slug)
if auth_key not in st.session_state:
    st.session_state[auth_key] = False

# ========================= عرض الملفات (روابط تنزيل) =========================
st.markdown("### الملفات الحالية (قراءة فقط) 🔐")
files = list_files(section_slug)
if not files:
    st.info("لا توجد ملفات بعد في هذا القسم. استخدم لوحة التحكم لرفع الملفات بعد إدخال كلمة المرور الصحيحة.")
else:
    for idx, (name, size, path) in enumerate(files, start=1):
        c1, c2 = st.columns([4,1])
        with c1:
            st.markdown(f"**#{idx} — {name}**  <span class='code-note'>({human_size(size)})</span>", unsafe_allow_html=True)
        with c2:
            with open(path, "rb") as fh:
                st.download_button("تنزيل", data=fh.read(), file_name=name, type="secondary", key=f"dl_{section_slug}_{idx}")

# ========================= لوحة التحكم (كلمة مرور + رفع) =========================
st.markdown("---")
st.markdown("### لوحة التحكم (تتطلب كلمة مرور القسم) 🔒")

# نموذج الدخول
with st.form(f"auth_form_{section_slug}"):
    pw_in = st.text_input("أدخل كلمة المرور", type="password", help="كلمة المرور الخاصة بالقسم المحدد في اليسار.")
    auth_btn = st.form_submit_button("دخول")
    if auth_btn:
        want = read_secret(PW_KEYS.get(section_slug, ""), "")
        if want and pw_in == want:
            st.session_state[auth_key] = True
            st.success(f"تم التحقق — أذونات الرفع مفعّلة لقسم «{section_ar}».")
        else:
            st.session_state[auth_key] = False
            st.error("كلمة المرور غير صحيحة.")

# زر خروج
col_a, col_b = st.columns([1,5])
with col_a:
    if st.session_state[auth_key]:
        if st.button("خروج من وضع الإدارة", type="secondary"):
            st.session_state[auth_key] = False
            st.experimental_rerun()

# نموذج الرفع (يظهر فقط بعد الدخول)
if st.session_state[auth_key]:
    st.info(f"مسموح برفع ملفات إلى قسم **{section_ar}**. الحد الأقصى {MAX_MB}MB لكل ملف. الصيغ: {', '.join(ACCEPT)}")

    with st.form(f"upload_form_{section_slug}", clear_on_submit=True):
        uploads = st.file_uploader(
            f"ارفع ملف/ملفات قسم {section_ar}",
            type=ACCEPT,
            accept_multiple_files=True,
            key=uploader_key(section_slug),
        )
        do_upload = st.form_submit_button("رفع الملفات")

    if do_upload and uploads:
        # فهرس الملفات الموجودة (اسم -> (حجم, بصمة))
        existing = {}
        for n, _, p in list_files(section_slug):
            try:
                existing[n] = (os.path.getsize(p), file_sha256(open(p, "rb").read()))
            except Exception:
                pass

        saved, skipped, oversized = 0, 0, 0

        for f in uploads:
            data = f.read()

            # 1) تحقق الحجم
            if len(data) > MAX_BYTES:
                oversized += 1
                st.error(f"❌ الملف **{f.name}** يتجاوز حد {MAX_MB}MB — لم يتم الحفظ.")
                continue

            # 2) بصمة المحتوى لمنع أي تكرار فعلي
            new_hash = file_sha256(data)

            # 3) هل يوجد ملف بنفس الاسم والحجم والبصمة؟ → تخطٍ
            same_exists = False
            if f.name in existing:
                size0, h0 = existing[f.name]
                if size0 == len(data) and h0 == new_hash:
                    same_exists = True

            if same_exists:
                skipped += 1
                continue

            # 4) تجهيز مسار الحفظ (اسم فريد عند التعارض)
            ensure_dir(section_dir)
            dest = os.path.join(section_dir, f.name)
            if os.path.exists(dest):
                base, ext = os.path.splitext(f.name)
                dest = os.path.join(section_dir, f"{base}_{datetime.now().strftime('%Y%m%d-%H%M%S')}{ext}")

            # 5) حفظ ذري (atomic) بقدر الإمكان
            tmp_path = dest + ".part"
            with open(tmp_path, "wb") as fh:
                fh.write(data)
            os.replace(tmp_path, dest)  # يستبدل إن وُجد بشكل ذري
            saved += 1

        # 6) رسائل الحالة
        if saved:
            st.success(f"👍 تم حفظ {saved} ملف/ملفات بنجاح.")
        if skipped:
            st.info(f"ℹ️ تم تخطي {skipped} ملف/ملفات لأنها مطابقة تمامًا لملفات محفوظة.")
        if oversized:
            st.warning(f"⚠️ {oversized} ملف/ملفات تم رفضها لأنها أكبر من {MAX_MB}MB.")

        # إعادة تحميل القائمة بعد الحفظ
        st.experimental_rerun()

# ========================= تذييل =========================
st.markdown(
    "<div class='footer'>تصميم وتطوير رئيس مهندسين أقدم <b class='gold'>طارق مجيد الكريمي</b> ©</div>",
    unsafe_allow_html=True,
)

# ========================= تذكير Secrets =========================
"""
إعدادات Secrets المتوقعة (مثال):

PW_POLICIES   = "policy-2025"
PW_OBJECTIVES = "obj-2025"
PW_DOCS       = "docs-2025"
PW_AUDIT      = "audit-2025"
PW_AUDITS     = "audits-2025"
PW_NC         = "nc-2025"
PW_CAPA       = "capa-2025"
PW_KB         = "kb-2025"
PW_REPORTS    = "reports-2025"
PW_KPI        = "kpi-2025"
PW_ESIGN      = "esign-2025"
PW_NOTIFY     = "notify-2025"
PW_RISKS      = "risks-2025"
"""
