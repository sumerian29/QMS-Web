# streamlit_app.py
# واجهة عربية كاملة مع ألوان الأزرق و RTL
import os
import base64
from datetime import datetime
from io import BytesIO

import streamlit as st
import pandas as pd

# -------------------------------
# إعداد الصفحة
# -------------------------------
st.set_page_config(
    page_title="منصة إدارة الجودة والأداء — QMS",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------
# تنسيق عام: RTL + ألوان
# (يبقى config.toml هو المصدر الرئيسي للألوان إن وُجد)
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] * {
  direction: rtl;
  text-align: right;
  font-family: 'Cairo', sans-serif;
}

/* خلفية عامة أزرق فاتح (احتياطي لو لم يوجد .streamlit/config.toml) */
[data-testid="stAppViewContainer"] {
  background: #EAF4FF;
}

/* الشريط الجانبي بدرجة أزرق أغمق */
[data-testid="stSidebar"] {
  background: #CFE3FF;
  border-left: 1px solid #BBD2FF;
}

/* أزرار أساسية */
:root { --primary-color: #0A66C2; }
button[kind="primary"] { background-color: #0A66C2; }

/* تحسين المسافات */
.block-container { padding-top: 1.2rem; padding-bottom: 1.6rem; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# تعريف الأقسام (تعريب كامل)
# ملاحظة: أبقينا مفاتيح slug كما هي كي لا تتأثر وظائفك السابقة
# -------------------------------
SECTIONS = {
    "سياسة الجودة":              {"slug": "policies",   "pw_key": "PW_POLICIES"},
    "الأهداف":                  {"slug": "objectives", "pw_key": "PW_OBJECTIVES"},
    "التحكم بالوثائق":          {"slug": "docs",       "pw_key": "PW_DOCS"},
    "خطة التدقيق":              {"slug": "audit_plan", "pw_key": "PW_AUDIT_PLAN"},
    "نتائج التدقيق":            {"slug": "audits",     "pw_key": "PW_AUDITS"},
    "عدم المطابقة":             {"slug": "nc",         "pw_key": "PW_NC"},
    "الإجراءات التصحيحية":      {"slug": "capa",       "pw_key": "PW_CAPA"},
    "قاعدة المعرفة":            {"slug": "kb",         "pw_key": "PW_KB"},
}

# -------------------------------
# رأس الصفحة (شعار + عنوان)
# -------------------------------
col_logo, col_title = st.columns([1, 5], gap="medium")
with col_logo:
    if os.path.exists("sold.png"):
        st.image("sold.png", caption="شعار الشركة", use_column_width=True)
with col_title:
    st.markdown("## منصة إدارة الجودة والأداء (QMS)")
    st.caption("Thi Qar Oil Company — واجهة عربية • أزرق فاتح مع قائمة جانبية بدرجة أغمق")

if os.path.exists("Audio.mp3"):
    with st.expander("تشغيل موسيقى ترحيبية (اختياري)"):
        st.audio("Audio.mp3")

st.markdown("---")

# -------------------------------
# الشريط الجانبي
# -------------------------------
st.sidebar.header("اختر القسم")
section_name = st.sidebar.selectbox("اختر القسم", list(SECTIONS.keys()))
st.sidebar.markdown("---")

query = st.sidebar.text_input("بحث سريع", placeholder="مثال: سياسة الجودة، التدقيق الداخلي، CAPA...")
st.sidebar.caption("© تصميم وتطوير: رئيس مهندسين طارق مجيد الكريمي")

# -------------------------------
# دوال مساعدة
# -------------------------------
def save_uploaded_file(uploaded_file, folder):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(upload
