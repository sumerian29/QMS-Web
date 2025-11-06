# --------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# --------------------------------------------------------

import os
from datetime import datetime
import streamlit as st

# =========================[ إعدادات عامة ]=========================
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# =======================[ أنماط وتنسيقات ]=========================
st.markdown("""
<style>
  :root{
    --tg-blue:#0a3d62;
    --tg-gold:#b8860b;
    --ink:#2c3e50;
    --muted:#6b7280;
    --bg:#f3f7fc;
    --card:#ffffff;
  }
  .stApp{background:var(--bg);}
  .block-container{padding-top:1.2rem; padding-bottom:1.2rem;}

  /* شريط الشهادة الذهبي */
  .iso-ribbon{
    background: linear-gradient(90deg, #c59d27, #f1c40f, #c59d27);
    color:#222;
    border-radius:14px;
    padding:10px 16px;
    text-align:center;
    font-weight:800;
    letter-spacing:.3px;
    box-shadow:0 4px 16px rgba(0,0,0,.08);
    margin: 10px auto 12px;
    max-width: 980px;
  }
  .iso-ribbon small{display:block; color:#333; font-weight:600; opacity:.9}

  /* صندوق شهادات/صور */
  .card{
    background:var(--card);
    border:1px solid #e6ebf2;
    border-radius:16px;
    padding:16px;
    box-shadow:0 6px 20px rgba(10,61,98,.06);
  }

  /* عناصر RTL داخل Select */
  .stSelectbox [data-baseweb="select"]{direction:rtl;}
</style>
""", unsafe_allow_html=True)

# دالة اسم ملف آمن
def safe_filename(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum() or ch in (" ", ".", "-", "_")).strip()

# ===================[ ترويسة: الشعار + العناوين ]==================
col_logo, col_title, _ = st.columns([1, 3, 1])

with col_logo:
    logo_path = os.path.join(os.path.dirname(__file__), "sold.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

with col_title:
    st.markdown(
        """
        <div style='text-align:center; line-height:1.8;'>
          <h1 style='color:#0a3d62; font-size:44px; font-weight:900; margin:0 0 6px 0;'>
            IMS — Integrated Management System
          </h1>
          <h2 style='color:#b8860b; font-size:36px; font-weight:900; margin:0 0 4px 0;'>
            شركة نفط ذي قار
          </h2>
          <h3 style='color:#2c3e50; font-size:26px; margin:4px 0 8px 0;'>
            شعبة الجودة وتقويم الأداء المؤسسي
          </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================[ شريط الشهادة الذهبي ]======================
st.markdown(
    """
    <div class="iso-ribbon">
      CERTIFIED ISO 9001:2015 — Bureau Veritas
      <small>Quality Management System — UKAS Accredited</small>
    </div>
    """,
    unsafe_allow_html=True
)

# ===================[ فقرة الإنجاز + صورة الشهادة ]=================
st.markdown(
    """
    <div class="card" style="max-width:980px; margin:0 auto 8px;">
      <p style="font-size:18px; color:#1e272e; font-weight:500; margin:2px 0 14px;">
        يُعَد حصول <strong>شركة نفط ذي قار</strong> على شهادة الاعتماد الدولي
        <strong>ISO 9001:2015</strong> إنجازًا وطنيًا واستراتيجيًا تجسّد بفضل
        جهود <strong>شعبة الجودة وتقويم الأداء المؤسسي</strong> في ترسيخ أنظمة
        الإدارة المتكاملة وتطبيق التحسين المستمر وتعزيز ثقافة الجودة في جميع التشكيلات.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

iso_img = os.path.join(os.path.dirname(__file__), "iso_cert.jpg")
if os.path.exists(iso_img):
    st.markdown("<div style='max-width:980px; margin:0 auto;'>", unsafe_allow_html=True)
    st.image(iso_img, use_column_width=True,
             caption="شهادة الاعتماد الممنوحة لشركة نفط ذي قار من شركة Bureau Veritas — 21 تموز 2025")
    st.markdown("</div>", unsafe_allow_html=True)

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

# كلمات المرور من Secrets (مع قيم افتراضية للتجربة)
def sec(key, default=""):
    try: return st.secrets[key]
    except Exception: return default

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

PLACEHOLDERS = {
    "Quality Policy":"policy-2025","Objectives":"obj-2025","Document Control":"docs-2025",
    "Audit Plan":"audit-2025","Audits":"audits-2025","Non-Conformance":"nc-2025",
    "CAPA":"capa-2025","Knowledge Base":"kb-2025","Reports":"reports-2025",
    "KPI":"kpi-2025","E-Sign":"esign-2025","Notify":"notify-2025","Risks":"risks-2025"
}

# ================ [ الشريط الجانبي: اختيار القسم ] ================
st.sidebar.markdown("<h4 style='text-align:right;'>اختر القسم</h4>", unsafe_allow_html=True)
selected_ar = st.sidebar.selectbox("اختر القسم", SECTIONS_AR, index=0)
section_key = SECTIONS_AR2EN[selected_ar]

# ===============[ عرض الملفات الحالية (قراءة فقط) ]================
st.markdown("### 📂 الملفات الحالية (قراءة فقط)")
files_root = os.path.join(os.path.dirname(__file__), "uploaded", section_key)
if os.path.isdir(files_root) and len(os.listdir(files_root)) > 0:
    items = sorted(os.listdir(files_root))
    for nm in items:
        full = os.path.join(files_root, nm)
        size = os.path.getsize(full)/1024/1024
        st.write(f"• **{nm}** — {size:.2f} MB")
else:
    st.info("لا توجد ملفات بعد في هذا القسم. استخدم لوحة التحكم لرفع الملفات بعد إدخال كلمة المرور الصحيحة.")

# ======================[ لوحة التحكم والباسوورد ]=====================
st.markdown("### 🔐 لوحة التحكم (تتطلب كلمة مرور القسم)")
entered_pw = st.text_input(
    f"أدخل كلمة المرور لقسم «{selected_ar}»",
    type="password",
    placeholder=f"مثال: {PLACEHOLDERS.get(section_key,'policy-2025')}"
)

if entered_pw:
    if entered_pw == PASSWORDS.get(section_key, ""):
        st.success("تم التحقق بنجاح — يمكنك رفع الملفات الآن.")
        st.caption(f"حد الرفع: {MAX_MB}MB لكل ملف. الصيغ: PDF, DOCX, XLSX")

        up_files = st.file_uploader(
            "ارفع الملفات هنا",
            type=["pdf", "docx", "xlsx"],
            accept_multiple_files=True
        )
        if up_files:
            os.makedirs(files_root, exist_ok=True)
            saved = 0
            for f in up_files:
                if f.size > MAX_BYTES:
                    st.error(f"❌ {f.name} يتجاوز {MAX_MB}MB — لم يتم حفظه.")
                    continue
                fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_filename(f.name)}"
                with open(os.path.join(files_root, fname), "wb") as out:
                    out.write(f.read())
                saved += 1
            if saved:
                st.success(f"✅ تم حفظ {saved} ملف(ات) داخل: uploaded/{section_key}")
                st.caption("تنبيه: التخزين داخل بيئة الاستضافة مؤقت. للحفظ الدائم نقترح ربط Google Drive لاحقًا.")
    else:
        st.error("كلمة المرور غير صحيحة. يرجى التحقق من قائمة كلمات المرور.")

# ===============================[ تذييل ]=============================
# ====== 1) CSS لضبط الفراغات ومنع قص الشعارات والتداخل ======
# ====== إنجاز وطني (نسخة aa) أعلى الصفحة ======
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
<style>
.ims-ann-card{
  max-width: 980px; margin: 20px auto 32px auto; padding: 22px 24px;
  background:#ffffff; border:1px solid #e6edf3; border-radius:16px;
  box-shadow: 0 2px 6px rgba(16,24,40,.04);
  direction: rtl; text-align: justify; line-height: 2.05;
}
.ims-ann-title{
  margin: 0 0 10px 0; text-align:center; font-size: 24px; font-weight: 800;
  color:#b58500; letter-spacing:.2px; border-bottom: 2px solid #e6c766; display:inline-block; padding-bottom:6px;
}
.ims-ann-body{ margin: 0; font-size: 17px; color:#0f172a }
.ims-iso{ color:#b58500; font-weight:800 }
.ims-bv{ font-weight:700 }
</style>
"""
st.markdown(aa_html, unsafe_allow_html=True)
# ====== نهاية إنجاز وطني ======
