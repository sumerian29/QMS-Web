# streamlit_app.py
# QMS Web — Thi Qar Oil Company
# تصميم وتطوير: رئيس مهندسين أقدم طارق مجيد الكريمي

import os, io, hashlib, csv
from datetime import datetime

import streamlit as st

# -------------------------------
# إعدادات عامة + تنسيق الألوان
# -------------------------------
st.set_page_config(page_title="QMS — Thi Qar Oil Company", layout="wide")

# ألوان الواجهة (يمكن تعديلها لاحقًا)
MAIN_BG   = "#eef6ff"   # أزرق فاتح للمحتوى
SIDEBAR_BG= "#e1effe"   # أزرق أغمق قليلًا للشريط الجانبي
TITLE_CLR = "#0f2b5b"   # عنوان داكن
ACCENT    = "#cba135"   # ذهبي للتفاصيل

# CSS بسيط لضبط الألوان والخط
st.markdown(f"""
<style>
  .stApp {{ background:{MAIN_BG}; }}
  section[data-testid="stSidebar"] {{ background:{SIDEBAR_BG}; }}
  h1, h2, h3, h4 {{ color:{TITLE_CLR}; }}
  .small-note {{ color:#666; font-size:14px; }}
  .gold {{ color:{ACCENT}; font-weight:600; }}
  .stDownloadButton button {{ width:100%; }}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# ثوابت وادوات مساعدة
# -------------------------------
MAX_MB = 200
MAX_BYTES = MAX_MB * 1024 * 1024

# خريطة الأقسام عربي ⇄ إنجليزي
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
    "التنبيهات": "Notify",
    "المخاطر": "Risks",        # ← أضف هذا السطر
}
SECTIONS_AR = [
    "سياسة الجودة","الأهداف","ضبط الوثائق","خطة التدقيق","نتائج التدقيق",
    "عدم المطابقة","الإجراءات التصحيحية والوقائية (CAPA)","قاعدة المعرفة",
    "التقارير","مؤشرات الأداء (KPI)","التواقيع الإلكترونية","التنبيهات",
    "المخاطر"  # ← وضّح ترتيب الظهور في القائمة
]


# قراءة كلمات المرور من Secrets إن وُجدت، وإلا الافتراضي
def sec(name, default):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)

PASSWORDS = {
    "Quality Policy":   sec("PW_POLICIES", "policy-2025"),
    "Objectives":       sec("PW_OBJECTIVES", "obj-2025"),
    "Document Control": sec("PW_DOCS", "docs-2025"),
    "Audit Plan":       sec("PW_AUDIT", "audit-2025"),
    "Audits":           sec("PW_AUDITS", "audits-2025"),
    "Non-Conformance":  sec("PW_NC", "nc-2025"),
    "CAPA":             sec("PW_CAPA", "capa-2025"),
    "Knowledge Base":   sec("PW_KB", "kb-2025"),
    "Reports":          sec("PW_REPORTS", "reports-2025"),
    "KPI":              sec("PW_KPI", "kpi-2025"),
    "E-Sign":           sec("PW_ESIGN", "esign-2025"),
    "Notify":           sec("PW_NOTIFY", "notify-2025"),
    "Risks":            sec("PW_RISKS", "risks-2025"),   # جديد
}

def normalize_pw(s: str) -> str:
    """تطبيع كلمة المرور لتلافي مشاكل النسخ/العربية/الشرطات"""
    s = str(s or "").strip()
    s = s.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))  # أرقام عربية → لاتينية
    for dash in ("–", "—", "−", "ـ"): s = s.replace(dash, "-")  # توحيد الشرطة
    for mark in ("\u200f","\u200e","\u202a","\u202b","\u202c","\u2066","\u2067","\u2068","\u2069"):
        s = s.replace(mark, "")
    s = s.replace(" ", "")
    return s.lower()

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_uploaded_file(uploaded_file, folder):
    ensure_dir(folder)
    path = os.path.join(folder, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def list_files(folder):
    """عرض الملفات (قراءة فقط) مع أزرار تنزيل"""
    if not os.path.isdir(folder):
        st.info("لا توجد ملفات بعد في هذا القسم.")
        return
    files = sorted(p for p in os.listdir(folder) if os.path.isfile(os.path.join(folder, p)))
    if not files:
        st.info("لا توجد ملفات بعد في هذا القسم.")
        return
    for name in files:
        fp = os.path.join(folder, name)
        with open(fp, "rb") as f:
            st.download_button(
                label=f"⬇️ تنزيل: {name}",
                data=f.read(),
                file_name=name,
                mime="application/octet-stream",
                use_container_width=True
            )

def audit_pw(section_key: str, success: bool, entered_pw: str):
    """تسجيل محاولات كلمات السر (نجاح/فشل) بدون تخزين النص الصريح"""
    ensure_dir("logs")
    log_path = os.path.join("logs", "auth_log.csv")
    masked = hashlib.sha256(normalize_pw(entered_pw).encode()).hexdigest()[:10]
    row = [datetime.now().isoformat(timespec="seconds"), section_key, "OK" if success else "FAIL", masked]
    new_file = not os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file: w.writerow(["timestamp","section","result","pw_hash"])
        w.writerow(row)

# -------------------------------
# الهيدر: الشعار + العناوين
# -------------------------------
col_logo, col_title = st.columns([1, 3], vertical_alignment="center")
with col_logo:
    # ضع صورة الشعار باسم sold.png داخل جذر المشروع
    try:
        st.image("sold.png", width=110)
    except Exception:
        st.write("")

with col_title:
    st.markdown(
        f"""
        <div style="margin-top:4px;">
            <h1 style="margin-bottom:0;">QMS — Quality & Performance Division</h1>
            <div style="color:{ACCENT}; font-weight:700; font-size:20px; margin-top:2px;">
                Thi Qar Oil Company
            </div>
            <div style="color:#333; font-size:18px; margin-top:8px;">
                <span class="gold">شعبة الجودة وتقويم الأداء المؤسسي</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# -------------------------------
# اختيار القسم (بالعربية)
# -------------------------------
st.sidebar.header("اختر القسم")
selected_ar = st.sidebar.selectbox("اختر القسم", SECTIONS_AR, index=0)
section_key = SECTIONS_AR2EN[selected_ar]            # المفتاح الإنجليزي
section_folder = os.path.join("uploads", section_key.replace(" ", "_"))

# -------------------------------
# عرض الملفات (متاح للجميع)
# -------------------------------
st.subheader("📂 الملفات الحالية (قراءة فقط)")
list_files(section_folder)

st.divider()

# -------------------------------
# رفع الملفات (يتطلب كلمة مرور)
# -------------------------------
st.subheader("لوحة التحكم (تتطلب كلمة مرور القسم) 🔒")
raw_pw = st.text_input("أدخل كلمة المرور", type="password", placeholder="مثال: policy-2025")
entered = normalize_pw(raw_pw)
expected = normalize_pw(PASSWORDS.get(section_key, ""))

if entered:
    if entered == expected:
        audit_pw(section_key, True, raw_pw)
        st.success("تم التحقق من كلمة المرور ✅ يمكنك رفع الملفات.")

        uploaded_files = st.file_uploader(
            f"ارفع ملفات قسم “{selected_ar}” (حد {MAX_MB}MB لكل ملف) • PDF, DOCX, XLSX",
            type=["pdf","docx","xlsx"],
            accept_multiple_files=True
        )

        if uploaded_files and st.button("رفع الملفات", type="primary", use_container_width=True):
            ok, too_big = 0, []
            for uf in uploaded_files:
                size = getattr(uf, "size", None)
                if size is not None and size > MAX_BYTES:
                    too_big.append(f"{uf.name} ({size/1024/1024:.1f}MB)")
                    continue
                save_uploaded_file(uf, section_folder)
                ok += 1
            if ok:
                st.success(f"تم رفع {ok} ملف/ملفات بنجاح ✅")
            if too_big:
                st.error(f"تم رفض هذه الملفات لتجاوزها {MAX_MB}MB: " + "، ".join(too_big))
    else:
        audit_pw(section_key, False, raw_pw)
        st.error("كلمة المرور غير صحيحة ❌")
else:
    st.info("المشاهدة متاحة للجميع. أدخل كلمة المرور لتفعيل الرفع.")

st.markdown("---")

# -------------------------------
# التوقيع الرسمي
# -------------------------------
st.markdown(
    f"""
    <div style='text-align:center; color:#444; font-size:18px;'>
        © تصميم وتطوير رئيس مهندسين أقدم
        <span style='color:{ACCENT}; font-weight:bold;'> طارق مجيد الكريمي</span>
    </div>
    """,
    unsafe_allow_html=True
)

