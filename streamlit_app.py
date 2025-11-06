# ---------------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ---------------------------------------------------------------

import os, io, base64, hashlib, shutil
from datetime import datetime
import streamlit as st

# ========== إعدادات عامة ==========
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# ===== CSS خفيف مع دعم العربية والهوية البصرية =====
st.markdown("""
<style>
:root { --brand:#0f3a5a; --gold1:#c89b0a; --gold2:#ad7e03; --bg:#eef4fb; }
html,body,[data-testid="stApp"]{ background:var(--bg); }
h1,h2,h3,h4,h5,h6, .st-emotion-cache-10trblm, .st-emotion-cache-1c7y2kd {
  font-family: "Segoe UI", Tahoma, Arial, sans-serif; direction: rtl; text-align: center;
}
.hero-wrap{ padding:8px 0 0; }
.hero-grid{ display:grid; grid-template-columns: 140px 1fr 140px; gap:8px; align-items:center;}
.logo{ width:140px; height:auto; margin-inline:auto; display:block; }
h1.title{ color:#0f3a5a; font-size:42px; line-height:1.2; margin:0 0 4px; }
h2.sub{ color:#d19a00; font-weight:800; letter-spacing:1px; margin:6px 0 2px; }
h3.division{ color:#0f3a5a; font-weight:700; margin:0 0 18px; }
.badge{ background: linear-gradient(90deg, var(--gold2), var(--gold1)); color:#102b3f;
  border-radius:14px; padding:12px 18px; font-weight:800; text-align:center; margin:0 auto 12px; width:min(1000px,95%);}
.card{ background:#fff; border:1px solid #e6eef6; border-radius:14px; padding:16px 18px; width:min(1100px,95%); margin:8px auto;}
.card h3{ color:#d19a00; margin:0 0 10px; border-bottom:2px solid #e8d28a; display:inline-block; padding-bottom:6px;}
.note{ color:#0f3a5a; font-size:13px; opacity:.85; text-align:center; margin-top:8px;}
.section-box{ background:#eef5ff; border:1px solid #d9e6f5; padding:12px 16px; border-radius:12px;}
.file-row{ display:flex; gap:10px; align-items:center; justify-content:space-between; border-bottom:1px dashed #e8eef6; padding:8px 0;}
.file-row:last-child{ border-bottom:none; }
a.dl{ text-decoration:none; background:#f6faff; border:1px solid #dce8f7; padding:4px 10px; border-radius:10px;}
input[type="password"]{ direction:ltr; }
.footer{ text-align:center; margin:24px 0 8px; color:#0f3a5a; font-weight:600;}
</style>
""", unsafe_allow_html=True)

# ===== مسارات حفظ البيانات =====
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRASH_DIR = os.path.join(BASE_DIR, "trash")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TRASH_DIR, exist_ok=True)

# ===== الأقسام (العربية ← مجلد) =====
SECTIONS_AR2EN = {
    "سياسة الجودة": "policy",
    "الأهداف": "objectives",
    "ضبط الوثائق": "doccontrol",
    "خطة التدقيق": "auditplan",
    "نتائج التدقيق": "audits",
    "عدم المطابقة": "nonconf",
    "الإجراءات التصحيحية والوقائية (CAPA)": "capa",
    "قاعدة المعرفة": "kb",
    "التقارير": "reports",
    "مؤشرات الأداء (KPI)": "kpi",
    "التوقيع الإلكتروني": "esign",
    "الإشعارات": "notify",
    "المخاطر": "risks",   # جديد
}
SECTIONS_AR = list(SECTIONS_AR2EN.keys())

# ===== كلمات المرور لكل قسم =====
PASSWORDS = {
    "policy": "policy-2025@",
    "objectives": "obj-2025@",
    "doccontrol": "doc-2025@",
    "auditplan": "plan-2025@",
    "audits": "audit-2025@",
    "nonconf": "nc-2025@",
    "capa": "capa-2025@",
    "kb": "kb-2025@",
    "reports": "rep-2025@",
    "kpi": "kpi-2025@",
    "esign": "esign-2025@",
    "notify": "notify-2025@",
    "risks": "risk-2025@",  # قسم المخاطر
}

# ===== دوال مساعدة =====
def ensure_dirs(slug: str):
    d = os.path.join(DATA_DIR, slug); t = os.path.join(TRASH_DIR, slug)
    os.makedirs(d, exist_ok=True); os.makedirs(t, exist_ok=True)
    return d, t

def sha256_of_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def save_if_new(folder: str, filename: str, content: bytes) -> tuple[bool, str]:
    """يحفظ الملف إن لم يكن موجوداً بنفس البصمة/الحجم. يعيد (تم_الحفظ, اسم_المسار)."""
    incoming_sig = sha256_of_bytes(content)
    for old in sorted(os.listdir(folder)):
        p = os.path.join(folder, old)
        try:
            with open(p, "rb") as r: 
                if sha256_of_bytes(r.read()) == incoming_sig:
                    return False, p
        except Exception:
            pass
    # اسم منسق #N — yyyymmdd_hhmmss — الاسم.ext
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    base, ext = os.path.splitext(filename)
    newname = f"{ts}—{base}{ext}".replace(" ", "_")
    path = os.path.join(folder, newname)
    with open(path, "wb") as w: w.write(content)
    return True, path

def file_download_link(path: str) -> str:
    name = os.path.basename(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<a class="dl" href="data:application/octet-stream;base64,{b64}" download="{name}">تنزيل</a>'

# ===== الشعار أعلى الصفحة =====
left_col, mid_col, right_col = st.columns([1,3,1])

with mid_col:
    st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="hero-grid">', unsafe_allow_html=True)
    # يسار الشبكة: شعار
    logo_shown = False
    logo_path = os.path.join(BASE_DIR, "sold.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=140)
        logo_shown = True
    else:
        # بديل HTML (في حال اختفى الملف) — نفس الاسم الذي أعطيته: sold.png
        st.markdown(
            '<img class="logo" src="https://raw.githubusercontent.com/sumerian29/QMS-Web/main/sold.png" onerror="this.style.display=\'none\'">',
            unsafe_allow_html=True
        )
    # وسط الشبكة: العناوين
    st.markdown("""
      <div>
        <h1 class="title">IMS — Integrated Management System</h1>
        <h2 class="sub">شركة نفط ذي قار</h2>
        <h3 class="division">شعبة الجودة وتقويم الأداء المؤسسي</h3>
      </div>
    """, unsafe_allow_html=True)
    # يمين الشبكة (فراغ جمالي)
    st.write("")
    st.markdown('</div></div>', unsafe_allow_html=True)

# ===== شريط شهادة ISO الذهبي =====
st.markdown(
    '<div class="badge">CERTIFIED ISO 9001:2015 — Bureau Veritas  ·  Quality Management System — UKAS Accredited</div>',
    unsafe_allow_html=True
)

# ===== بطاقة الإنجاز الوطني =====
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>إنجاز وطني لشركة نفط ذي قار</h3>', unsafe_allow_html=True)
    st.write(
        "يُعَد حصول شركة نفط ذي قار على شهادة الاعتماد الدولي ISO 9001:2015 من مؤسسة "
        "Bureau Veritas البريطانية إنجازًا وطنيًا واستراتيجيًا، تحقق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي "
        "في ترسيخ أنظمة الإدارة المتكاملة وتطبيق مفاهيم التحسين المستمر وتعزيز ثقافة الجودة في جميع تشكيلات الشركة، "
        "دعمًا لمسيرتها نحو التميز والشفافية والالتزام بأعلى المعايير العالمية."
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ===== صورة الشهادة (المعامل الصحيح use_column_width) =====
CERT_PATH = os.path.join(BASE_DIR, "iso_cert.jpg")
if os.path.exists(CERT_PATH):
    st.image(CERT_PATH, caption="نسخة من شهادة المنح — Bureau Veritas — 2025 تموز", use_column_width=True)
else:
    st.info("📄 لم يتم العثور على ملف الشهادة iso_cert.jpg في المستودع. تأكد من وجوده في جذر المشروع.")

st.markdown('<div class="note">استخدم القائمة اليمنى لاختيار القسم.</div>', unsafe_allow_html=True)

# ===== اختيار القسم =====
st.sidebar.markdown("### اختر القسم")
section_ar = st.sidebar.selectbox("اختر", SECTIONS_AR, index=SECTIONS_AR.index("سياسة الجودة"))
slug = SECTIONS_AR2EN[section_ar]
data_dir, trash_dir = ensure_dirs(slug)

st.divider()

# ===== عرض الملفات الحالية (روابط فقط) =====
st.markdown("### الملفات الحالية (قراءة فقط) 🔒")
box = st.container()
files = sorted(os.listdir(data_dir))
if not files:
    box.markdown('<div class="section-box">لا توجد ملفات بعد في هذا القسم.</div>', unsafe_allow_html=True)
else:
    for i, fn in enumerate(files, start=1):
        path = os.path.join(data_dir, fn)
        link = file_download_link(path)
        box.markdown(f"""
        <div class="file-row">
          <div>#{i} — {fn}</div>
          <div>{link}</div>
        </div>
        """, unsafe_allow_html=True)

# ===== لوحة التحكم (تتطلب كلمة مرور) =====
st.markdown("### لوحة التحكم (تتطلب كلمة مرور القسم) 🔐")
pw = st.text_input("أدخل كلمة المرور", type="password", value=st.session_state.get("last_pw", ""))
enter = st.button("دخول")

authorized = False
if enter:
    st.session_state["last_pw"] = pw
    if PASSWORDS.get(slug) == pw.strip():
        authorized = True
        st.success("تم التحقق من كلمة المرور بنجاح. بإمكانك الرفع والحذف لهذا القسم.")
    else:
        st.error("كلمة المرور غير صحيحة لهذا القسم.")

if authorized:
    # --- الرفع (منع التكرار الحقيقي) ---
    st.markdown("#### رفع ملف إلى هذا القسم")
    up = st.file_uploader("اختر ملفًا (PDF, DOCX, XLSX, PNG, JPG…)", type=None, key=f"uploader_{slug}")
    if up is not None:
        content = up.read()
        # أمنع إعادة الحفظ عند إعادة التشغيل: قارن مع آخر بصمة رفعت
        last_sig_key = f"last_sig_{slug}"
        sig = sha256_of_bytes(content)
        if st.session_state.get(last_sig_key) == sig:
            st.info("تمت معالجة هذا الملف بالفعل في هذه الجلسة.")
        else:
            saved, saved_path = save_if_new(data_dir, up.name, content)
            st.session_state[last_sig_key] = sig
            if saved:
                st.success("تم الحفظ بنجاح.")
            else:
                st.warning("هذا الملف موجود مسبقًا (نفس المحتوى). لم يتم إنشاء نسخة مكررة.")

    # --- سلة المحذوفات / الحذف الانتقائي أو الجماعي ---
    st.markdown("#### حذف جماعي (نقل إلى سلة المحذوفات)")
    current = sorted(os.listdir(data_dir))
    if current:
        to_remove = st.multiselect("اختر الملفات:", current, key=f"sel_{slug}")
        colA, colB = st.columns([1,2])
        if colA.button("حذف الملفات المحددة"):
            cnt = 0
            for name in to_remove:
                src = os.path.join(data_dir, name)
                dst = os.path.join(trash_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}—{name}")
                try:
                    shutil.move(src, dst); cnt += 1
                except Exception as e:
                    st.error(f"تعذر نقل {name} إلى سلة المحذوفات: {e}")
            if cnt:
                st.success(f"تم نقل {cnt} ملف/ملفات إلى سلة المحذوفات.")
                st.info("↻ قم بتحديث الصفحة أو اختر القسم مرة أخرى لتحديث القائمة.")
    else:
        st.info("لا توجد ملفات لحذفها في هذا القسم.")

# ===== تذييل =====
st.markdown('<div class="footer">تصميم وتطوير رئيس مهندسين أقدم طارق مجيد الكريمي</div>', unsafe_allow_html=True)
