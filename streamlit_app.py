# streamlit_app.py
# IMS — Integrated Management System (Arabic UI) for Thi Qar Oil Company
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi

import os
import io
import hashlib
import shutil
from datetime import datetime
from typing import List

import streamlit as st
from PIL import Image

# =========================
# إعدادات عامة للصفحة
# =========================
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# =========================
# أدوات مساعدة
# =========================

BASE_DIR = os.getcwd()

UPLOAD_BASE = os.path.join(BASE_DIR, "uploads")          # uploads/<slug>/
DELETED_BASE = os.path.join(BASE_DIR, "deleted")          # deleted/<slug>/

# الامتدادات المسموحة
ALLOWED_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg"}

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def safe_name(name: str) -> str:
    # حذف المحارف المزعجة
    bad = r'\/:*?"<>|'
    for ch in bad:
        name = name.replace(ch, " ")
    return "_".join(name.split())

def list_files(dir_path: str) -> List[str]:
    if not os.path.exists(dir_path):
        return []
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    # ترتيب تنازلي حسب تاريخ التعديل
    files.sort(key=lambda f: os.path.getmtime(os.path.join(dir_path, f)), reverse=True)
    return files

def readable_size(bytes_num: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_num < 1024:
            return f"{bytes_num:.1f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.1f} TB"

def ext_of(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

# =========================
# الأقسام + كلمات السر من Secrets
# =========================

# خريطة الأقسام عربي → slug إنجليزي
SECTIONS_AR2EN = {
    "سياسة الجودة": "policies",
    "الأهداف": "objectives",
    "ضبط الوثائق": "docs",
    "خطة التدقيق": "audit_plan",
    "التدقيقات": "audits",
    "عدم المطابقة": "nc",
    "الإجراءات التصحيحية والوقائية (CAPA)": "capa",
    "قاعدة المعرفة": "kb",
    "التقارير": "reports",
    "مؤشرات الأداء (KPI)": "kpi",
    "الإشعار": "notify",
    "المخاطر": "risks",  # جديد
}

SECTIONS_AR = list(SECTIONS_AR2EN.keys())

# أسماء مفاتيح كلمات المرور داخل secrets (يمكن تعديلها من صفحة Secrets في Streamlit)
# مثال القيم:
# PW_POLICIES = "policy-2025"
# PW_DOCS     = "docs-2025"
# ...
PW_KEYS = {
    "policies": st.secrets.get("PW_POLICIES", ""),
    "objectives": st.secrets.get("PW_OBJECTIVES", ""),
    "docs": st.secrets.get("PW_DOCS", ""),
    "audit_plan": st.secrets.get("PW_AUDIT", ""),     # خطة التدقيق
    "audits": st.secrets.get("PW_AUDITS", ""),
    "nc": st.secrets.get("PW_NC", ""),
    "capa": st.secrets.get("PW_CAPA", ""),
    "kb": st.secrets.get("PW_KB", ""),
    "reports": st.secrets.get("PW_REPORTS", ""),
    "kpi": st.secrets.get("PW_KPI", ""),
    "notify": st.secrets.get("PW_NOTIFY", ""),
    "risks": st.secrets.get("PW_RISKS", ""),          # جديد
}

# =========================
# تهيئة حالة الجلسة
# =========================
if "authed_sections" not in st.session_state:
    st.session_state.authed_sections = set()  # مجموعة الأقسام المسموح بها في هذه الجلسة

if "current_section_ar" not in st.session_state:
    st.session_state.current_section_ar = SECTIONS_AR[0]

# =========================
# رأس الصفحة — الشعار والعناوين
# =========================

# CSS بسيط
st.markdown(
    """
    <style>
      body, .stApp { background-color:#eef3f9; }
      .hero-grid { display:grid; grid-template-columns: 110px 1fr; gap:16px; align-items:center; }
      .logo { width: 100px; height: 100px; object-fit: contain; }
      h1.title { font-size:44px; margin:0; color:#133a5e; text-align:center; }
      h2.ar { font-size:34px; margin:4px 0 0; color:#b6860a; text-align:center; }
      h3.sub  { font-size:22px; color:#133a5e; text-align:center; margin-top:2px;}
      .gold { background: linear-gradient(90deg, #caa21e, #9d7410); color:#09263d;
              border-radius:16px; padding:14px 20px; font-weight:700; text-align:center;
              border:1px solid rgba(0,0,0,.1); }
      .card { background:white; border:1px solid #d7e2ee; padding:18px; border-radius:14px; }
      .muted { color:#315b7a; font-weight:500; }
      .footer { text-align:center; margin-top:30px; color:#6b7f93; }
      .download-btn { float:left; }
      .section-title { font-size:22px; }
      .badge { display:inline-block; padding:4px 8px; border-radius: 8px; background:#f0f6ff; border:1px solid #d5e3f5; color:#264a72; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True
)

# شبكة الرأس
colA, colB, colC = st.columns([1,3,1])
with colB:
    st.markdown('<div class="hero-grid">', unsafe_allow_html=True)

    # الشعار من sold.png (محلي)
    LOGO_PATH = "sold.png"
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, output_format="PNG", width=100)
    else:
        # لو الملف مفقود، نظهر عنصر فارغ
        st.markdown('<div style="width:100px; height:100px;"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div>
          <h1 class="title">IMS — Integrated Management System</h1>
          <h2 class="ar">شركة نفط ذي قار</h2>
          <h3 class="sub">شعبة الجودة وتقويم الأداء المؤسسي</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

# شريط ذهبي لمعلومات الاعتماد
st.markdown(
    '<div class="gold">CERTIFIED ISO 9001:2015 — Bureau Veritas &nbsp; · &nbsp; '
    'Quality Management System — UKAS Accredited</div>',
    unsafe_allow_html=True,
)

# بطاقة إنجاز وطني
with st.container():
    st.markdown(
        """
        <div class="card">
          <div class="section-title" style="text-align:center; color:#b6860a; font-weight:800;">
            إنجاز وطني لشركة نفط ذي قار
          </div>
          <p class="muted" style="line-height:1.9; text-align:justify;">
            يُعَد حصول شركة نفط ذي قار على شهادة الاعتماد الدولي <b>ISO 9001:2015</b>
            من مؤسسة <b>Bureau Veritas</b> البريطانية إنجازًا وطنيًا واستراتيجيًا،
            تحقق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي
            في ترسيخ أنظمة الإدارة المتكاملة وتطبيق مفاهيم التحسين المستمر
            وتعزيز ثقافة الجودة في جميع تشكيلات الشركة، دعمًا لمسيرتها نحو
            التميز والشفافية والالتزام بأعلى المعايير العالمية.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# شهادة المنح — عرض آمن
def show_certificate(cert_path: str):
    if os.path.exists(cert_path):
        try:
            img = Image.open(cert_path)
            st.image(img, caption="نسخة من شهادة المنح — Bureau Veritas — 2025 تموز", use_container_width=True)
        except Exception as e:
            st.warning(f"تعذّر عرض شهادة المنح. تحقق من نوع الملف/سلامته. التفاصيل: {e}")
    else:
        st.info("لم يتم العثور على ملف الشهادة (iso_cert.jpg). ضع الملف في جذر المستودع أو عدّل CERT_PATH.")

CERT_PATH = "iso_cert.jpg"
show_certificate(CERT_PATH)

st.divider()

# =========================
# واجهة اختيار القسم
# =========================
left, main = st.columns([1, 3])

with left:
    st.markdown("### اختر القسم")
    st.markdown('<span class="badge">اختر</span>', unsafe_allow_html=True)
    chosen_ar = st.selectbox("اختر القسم", SECTIONS_AR, index=SECTIONS_AR.index(st.session_state.current_section_ar))
    st.session_state.current_section_ar = chosen_ar
    slug = SECTIONS_AR2EN[chosen_ar]

with main:
    st.markdown("### الملفات الحالية (قراءة فقط) 📁")
    section_dir = os.path.join(UPLOAD_BASE, slug)
    ensure_dir(section_dir)

    files = list_files(section_dir)

    if not files:
        st.info("لا توجد ملفات بعد في هذا القسم.")
    else:
        # روابط تنزيل فقط، بدون عرض مباشر
        for idx, fn in enumerate(files, start=1):
            full_path = os.path.join(section_dir, fn)
            size = readable_size(os.path.getsize(full_path))
            # زر تنزيل
            with open(full_path, "rb") as f:
                st.download_button(
                    label=f"تنزيل",
                    data=f.read(),
                    file_name=fn,
                    mime="application/octet-stream",
                    key=f"dwn_{slug}_{fn}",
                    help="تنزيل الملف"
                )
            st.write(f"**#{idx} — {fn}**  _(الحجم: {size})_")
        st.caption("عرض روابط تنزيل فقط لتفادي تمدّد الصفحة مع كثرة الملفات.")

    st.divider()

    # =========================
    # لوحة التحكم (محمية بكلمة مرور)
    # =========================
    st.markdown("### لوحة التحكم (تتطلب كلمة مرور القسم) 🔒")

    # نموذج إدخال كلمة السر + زر دخول
    with st.form(key=f"auth_form_{slug}", clear_on_submit=False):
        pwd = st.text_input("أدخل كلمة المرور", type="password", help="أدخل كلمة المرور الصحيحة لهذا القسم")
        auth = st.form_submit_button("دخول")
        if auth:
            if PW_KEYS.get(slug, "") and pwd == PW_KEYS[slug]:
                st.session_state.authed_sections.add(slug)
                st.success("تم التحقق بنجاح — تم فتح لوحة التحكم.")
            else:
                st.error("كلمة المرور غير صحيحة.")

    authed = slug in st.session_state.authed_sections

    # نموذج الرفع والحذف يظهر فقط عند التحقق
    if authed:
        st.success("لوحة التحكم مفعّلة لهذا القسم.")
        st.markdown("#### رفع ملف إلى هذا القسم")

        uploaded_file = st.file_uploader("اختر ملفًا (PDF, DOCX, XLSX, PNG, JPG, ...). الحد الأقصى 200MB لكل ملف.", type=None)

        do_save = st.button("حفظ الملف", type="primary", help="رفع الملف وحفظه في هذا القسم")

        if do_save:
            if uploaded_file is None:
                st.warning("يرجى اختيار ملف أولاً.")
            else:
                ext = ext_of(uploaded_file.name)
                if ext not in ALLOWED_EXT:
                    st.error("نوع الملف غير مسموح.")
                else:
                    # قراءة bytes لبناء بصمة
                    file_bytes = uploaded_file.read()
                    uploaded_file.seek(0)

                    # منع التكرار: نفس الاسم أو نفس البصمة
                    # 1) الاسم
                    target_name = safe_name(uploaded_file.name)
                    target_path = os.path.join(section_dir, target_name)
                    if os.path.exists(target_path):
                        st.error("يوجد ملف بنفس الاسم داخل هذا القسم. غيّر الاسم أو احذف الملف الحالي.")
                    else:
                        # 2) البصمة
                        new_hash = file_hash(file_bytes)
                        duplicate = False
                        for existing in files:
                            ex_path = os.path.join(section_dir, existing)
                            try:
                                with open(ex_path, "rb") as exf:
                                    if file_hash(exf.read()) == new_hash:
                                        duplicate = True
                                        break
                            except Exception:
                                pass
                        if duplicate:
                            st.error("تم العثور على ملف مطابق (نفس المحتوى) داخل هذا القسم. تم إيقاف الحفظ.")
                        else:
                            # تسمية قياسية: رقم تسلسلي + تاريخ + الاسم
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            serial = len(files) + 1
                            final_name = f"{serial:03d}—{timestamp}—{target_name}"
                            final_path = os.path.join(section_dir, final_name)
                            try:
                                with open(final_path, "wb") as f:
                                    f.write(file_bytes)
                                st.success("تم الحفظ بنجاح.")
                            except Exception as e:
                                st.error(f"تعذّر الحفظ: {e}")

        st.divider()

        st.markdown("#### حذف جماعي (نقل إلى سلة المحذوفات)")
        current_files = list_files(section_dir)
        if not current_files:
            st.info("لا توجد ملفات لحذفها.")
        else:
            # اختيار عدة ملفات
            to_delete = st.multiselect("اختر الملفات:", current_files, help="اختر ملفًا أو أكثر لنقلهم إلى سلة المحذوفات")
            if st.button("نقل الملفات المحددة إلى سلة المحذوفات", help="لا يتم الحذف النهائي — يمكن استرجاع الملفات من مجلد deleted"):
                if not to_delete:
                    st.warning("لم تُحدد أي ملفات.")
                else:
                    trash_dir = os.path.join(DELETED_BASE, slug)
                    ensure_dir(trash_dir)
                    moved = 0
                    for name in to_delete:
                        src = os.path.join(section_dir, name)
                        dst = os.path.join(trash_dir, name)
                        if os.path.exists(src):
                            try:
                                shutil.move(src, dst)
                                moved += 1
                            except Exception as e:
                                st.error(f"تعذّر نقل {name}: {e}")
                    st.success(f"تم نقل {moved} ملف/ملفات إلى سلة المحذوفات.")
                    st.info("لتحديث القائمة، أعد تحميل الصفحة (CTRL+R) أو غيّر القسم ثم أعده.")

    else:
        st.info("أدخل كلمة المرور الصحيحة واضغط [دخول] لتفعيل لوحة التحكم.")

# تذييل لطيف
st.markdown(
    '<div class="footer">تصميم وتطوير رئيس مهندسين أقدم <b>طارق مجيد الكريمي</b></div>',
    unsafe_allow_html=True
)
