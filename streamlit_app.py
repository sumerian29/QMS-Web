# --------------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# --------------------------------------------------------------

import os
import base64
import streamlit as st
from datetime import datetime
from io import BytesIO

# --------------------------------------------------------------
# إعدادات عامة
# --------------------------------------------------------------
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# --------------------------------------------------------------
# تصميم الخلفية والألوان
# --------------------------------------------------------------
st.markdown("""
<style>
body, .stApp {
    background-color: #f3f7fc;
    direction: rtl;
    font-family: "Amiri", serif;
}
h1, h2, h3 {
    text-align: center;
    color: #0d3b66;
}
.gold-text {
    color: #c89b2d;
    text-align: center;
    font-size: 26px;
    font-weight: bold;
    border-bottom: 2px solid #c89b2d;
    display: inline-block;
    padding-bottom: 5px;
}
.section-box {
    background-color: white;
    border-radius: 15px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}
.footer {
    text-align: center;
    color: #444;
    margin-top: 30px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# الشعار والعنوان الرئيسي
# --------------------------------------------------------------
col1, col2 = st.columns([1, 4])
with col1:
    st.image("sold.png", width=150)
with col2:
    st.markdown("<h1>IMS — Integrated Management System</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='gold-text'>شركة نفط ذي قار</h2>", unsafe_allow_html=True)
    st.markdown("<h3>شعبة الجودة وتقويم الأداء المؤسسي</h3>", unsafe_allow_html=True)

# --------------------------------------------------------------
# فقرة إنجاز وطني لشركة نفط ذي قار
# --------------------------------------------------------------
st.markdown("""
<div style='text-align: center; margin-top: 20px;'>
  <h4 class='gold-text'>إنجاز وطني لشركة نفط ذي قار</h4>
  <p style='text-align: justify; direction: rtl; font-size:18px; line-height: 1.8;'>
  يُعَد حصول <b>شركة نفط ذي قار</b> على شهادة الاعتماد الدولي 
  <b style="color:#c89b2d;">ISO 9001:2015</b> 
  من مؤسسة <b>Bureau Veritas</b> البريطانية إنجازًا وطنيًا واستراتيجيًا، 
  تحقق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي في ترسيخ أنظمة الإدارة المتكاملة 
  وتطبيق مفاهيم التحسين المستمر وتعزيز ثقافة الجودة في جميع تشكيلات الشركة، 
  دعمًا لمسيرتها نحو التميز والشفافية والالتزام بأعلى المعايير العالمية.
  </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# شهادة الاعتماد (صورة)
# --------------------------------------------------------------
st.image("iso_cert.jpg", use_column_width=True)

# --------------------------------------------------------------
# اختيار القسم
# --------------------------------------------------------------
st.sidebar.header("اختر القسم")
section = st.sidebar.selectbox("اختر", [
    "سياسة الجودة",
    "الأهداف",
    "نتائج التدقيق",
    "الإجراءات",
    "المخاطر",
    "مؤشرات الأداء",
    "التقارير"
])

st.divider()

# --------------------------------------------------------------
# الملفات الحالية
# --------------------------------------------------------------
st.subheader("📂 الملفات الحالية (قراءة فقط)")

# مجلد رفع الملفات لكل قسم
upload_dir = f"uploads/{section}"
os.makedirs(upload_dir, exist_ok=True)
files = os.listdir(upload_dir)

if files:
    for f in files:
        file_path = os.path.join(upload_dir, f)
        with open(file_path, "rb") as file:
            file_bytes = file.read()
            b64 = base64.b64encode(file_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{f}" target="_blank">📄 {f}</a>'
            st.markdown(href, unsafe_allow_html=True)
else:
    st.info("لا توجد ملفات بعد في هذا القسم.")

# --------------------------------------------------------------
# لوحة التحكم
# --------------------------------------------------------------
st.subheader("🔒 لوحة التحكم (تتطلب كلمة مرور القسم)")

pw_input = st.text_input("أدخل كلمة المرور", type="password", placeholder="مثال: policy-2025")

# كلمات المرور
PASSWORDS = {
    "سياسة الجودة": "policy-2025",
    "الأهداف": "obj-2025",
    "نتائج التدقيق": "audit-2025",
    "الإجراءات": "docs-2025",
    "المخاطر": "risk-2025",
    "مؤشرات الأداء": "kpi-2025",
    "التقارير": "reports-2025"
}

# --------------------------------------------------------------
# رفع الملفات عند إدخال كلمة المرور الصحيحة
# --------------------------------------------------------------
if pw_input == PASSWORDS.get(section):
    uploaded_file = st.file_uploader("📤 اختر ملفًا لرفعه", type=["pdf", "docx", "xlsx", "pptx", "jpg", "png"])
    if uploaded_file is not None:
        save_path = os.path.join(upload_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ تم رفع الملف بنجاح: {uploaded_file.name}")

        # رابط فتح أو تنزيل الملف
        file_bytes = uploaded_file.getvalue()
        b64 = base64.b64encode(file_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{uploaded_file.name}" target="_blank">📄 فتح أو تنزيل {uploaded_file.name}</a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.warning("🔑 أدخل كلمة المرور الصحيحة لرفع الملفات إلى هذا القسم.")

# --------------------------------------------------------------
# التوقيع
# --------------------------------------------------------------
st.markdown("<div class='footer'>تصميم وتطوير رئيس مهندسين أقدم <b style='color:#c89b2d;'>طارق مجيد الكريمي</b></div>", unsafe_allow_html=True)
