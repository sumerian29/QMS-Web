import streamlit as st
import os
from github import Github
from io import BytesIO

# ==============================
# إعدادات الصفحة العامة
# ==============================
st.set_page_config(page_title="QMS — Thi Qar Oil Company", layout="wide")

# ==============================
# تنسيق الواجهة (الألوان والخطوط)
# ==============================
st.markdown("""
    <style>
        body {
            direction: rtl;
            font-family: 'Amiri', serif;
        }
        .title {
            text-align: center;
            color: #003366;
            font-size: 40px;
            font-weight: bold;
        }
        .subtitle {
            text-align: center;
            color: #CBA135;
            font-size: 22px;
            font-family: 'Amiri', serif;
        }
        .stSelectbox label {
            font-weight: bold;
            color: #003366;
        }
        .upload-label {
            font-weight: bold;
            color: #005588;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# عنوان الصفحة والشعار
# ==============================
st.image("sold.png", width=160)
st.markdown("<div class='title'>QMS — Quality & Performance Division</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Thi Qar Oil Company</div>", unsafe_allow_html=True)
st.divider()

# ==============================
# قائمة الأقسام
# ==============================
sections = {
    "Quality Policy": "سياسة الجودة",
    "Objectives": "الأهداف",
    "Document Control": "ضبط الوثائق",
    "Audit Plan": "خطة التدقيق",
    "Audits": "نتائج التدقيق",
    "Non-Conformance": "عدم المطابقة",
    "CAPA": "الإجراءات التصحيحية والوقائية",
    "Knowledge Base": "قاعدة المعرفة"
}

selected_section = st.sidebar.selectbox("اختر القسم", list(sections.keys()), format_func=lambda x: sections[x])

# ==============================
# تحميل الملفات وحفظها
# ==============================
def save_uploaded_file(uploaded_file, folder):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

# ==============================
# الواجهة الرئيسية لكل قسم
# ==============================
st.header(sections[selected_section])

uploaded_file = st.file_uploader(f"ارفع ملف {sections[selected_section]}", type=["pdf", "docx", "xlsx"])

if uploaded_file and st.button("رفع الملف", type="primary"):
    path = save_uploaded_file(uploaded_file, f"uploads/{selected_section}")
    st.success(f"✅ تم رفع الملف بنجاح: **{uploaded_file.name}**")
    st.info(f"📂 تم حفظه في: `{path}`")

# ==============================
# منطقة التحكم المحمية
# ==============================
st.divider()
st.subheader("🔒 لوحة التحكم (تتطلب كلمة مرور القسم)")

password = st.text_input("أدخل كلمة المرور", type="password")

if password == "QMS@ThiQar":
    st.success("تم تسجيل الدخول بنجاح ✅")
    st.write("يمكنك الآن إدارة الملفات والمجلدات الخاصة بالقسم.")
else:
    if password:
        st.error("❌ كلمة المرور غير صحيحة")

