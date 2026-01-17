# ------------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ------------------------------------------------------------

import os
import io
import base64
from datetime import datetime
from typing import List, Tuple, Dict, Optional

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# ================= App setup =================
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# ================= Styling ===================
st.markdown(
    """
<style>
  .stApp { background:#f3f7fb; }
  .hero-wrap{padding:16px 0 6px;}
  .hero-grid{
    display:grid;grid-template-columns:120px 1fr;gap:16px;
    align-items:center;justify-content:center;max-width:980px;margin:0 auto;
  }
  .logo{width:110px}
  .ttl {text-align:center}
  .ttl h1{margin:0;color:#123b57;font-size:44px;line-height:1.1;font-weight:800}
  .ttl h2{margin:10px 0 0;color:#b8860b;font-weight:800;font-size:34px}
  .ttl h3{margin:4px 0 0;color:#0f2740;font-weight:800;font-size:22px}
  .gold {background:linear-gradient(90deg,#b8860b,#cca642,#b8860b);
         color:#13233a;padding:12px 18px;border-radius:12px;font-weight:800;
         text-align:center;max-width:980px;margin:14px auto;}
  .card{background:#fff;border:1px solid #e9eef5;border-radius:14px;
        padding:14px 18px;max-width:980px;margin:10px auto;}
  .muted{color:#6b7280;font-size:13px}
  .sig{ text-align:center; color:#a07605; font-weight:700; margin:10px 0 0;}
  .cert {max-width:980px;margin:12px auto 6px;border-radius:12px;overflow:hidden;
         border:1px solid #e6ebf2; background:#fff;}
  .cert-caption{max-width:980px;margin:4px auto 18px;text-align:center;color:#6b7280;font-size:13px}
</style>
""",
    unsafe_allow_html=True,
)

# ================= Header =============
CERT_PATH = "iso_cert.jpg"
LOGO_PATH = "sold.png"

@st.cache_data
def inline_logo_src(path: str = "sold.png") -> str:
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    except Exception:
        return ""

st.markdown("<div class='hero-wrap'>", unsafe_allow_html=True)
colA, colB, colC = st.columns([1, 3, 1])
with colB:
    logo_src = inline_logo_src(LOGO_PATH)
    st.markdown(
        f"""
        <div class='hero-grid'>
          <img class='logo' src="{logo_src}">
          <div class='ttl'>
            <h1>IMS — Integrated Management System</h1>
            <h2>شركة نفط ذي قار</h2>
            <h3>شعبة الجودة وتقويم الأداء المؤسسي</h3>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='gold'>CERTIFIED ISO 9001:2015 — Bureau Veritas · Quality Management System — UKAS Accredited</div>",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class='card' style='text-align:center'>
يُعَد حصول شركة نفط ذي قار على شهادة الاعتماد الدولي <b>ISO 9001:2015</b> من مؤسسة <b>Bureau Veritas</b>
إنجازًا وطنيًا واستراتيجيًا، تحقق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي في ترسيخ أنظمة الإدارة المتكاملة
وتطبيق مفاهيم التحسين المستمر وتعزيز ثقافة الجودة في جميع تشكيلات الشركة، دعمًا لمسيرتها نحو التميز والشفافية
والالتزام بأعلى المعايير العالمية.
</div>
""",
    unsafe_allow_html=True,
)

if os.path.exists(CERT_PATH):
    st.image(CERT_PATH, use_container_width=True)

st.divider()

# ================= Sections ======
SECTIONS = {
    "سياسة الجودة": "policies",
    "الأهداف": "objectives",
    "ضبط الوثائق": "docs",
    "خطة التدقيق": "audit-plan",
    "نتائج التدقيق": "audits",
    "عدم المطابقة": "nc",
    "الإجراءات التصحيحية والوقائية (CAPA)": "capa",
    "قاعدة المعرفة": "kb",
    "التقارير": "reports",
    "مؤشرات الأداء (KPI)": "kpi",
    "التوقيع الإلكتروني": "esign",
    "الإشعارات": "notify",
    "المخاطر": "risks",
}

# ================= Sidebar =================
st.sidebar.markdown("### اختر القسم")
sec_ar = st.sidebar.selectbox("اختر", list(SECTIONS.keys()), key="section_select")
slug = SECTIONS[sec_ar]

st.sidebar.markdown("### صلاحيات القسم")

# قراءة كلمة المرور
password_key = f"PW_{slug.upper().replace('-', '_')}"
sec_secret = st.secrets.get(password_key, "")

pw = st.sidebar.text_input(
    "كلمة المرور (للرفع والحذف فقط)",
    type="password",
    key=f"pw_{slug}",
    value=""
)

if st.sidebar.button("دخول", key=f"enter_{slug}"):
    if not sec_secret:
        st.sidebar.error(f"❌ المفتاح '{password_key}' غير موجود في الأسرار.")
    elif not pw:
        st.sidebar.error("❌ الرجاء إدخال كلمة المرور.")
    elif pw.strip() == str(sec_secret).strip():
        st.session_state[f"auth_{slug}"] = True
        st.sidebar.success("✅ تم التحقق من كلمة المرور.")
        st.rerun()
    else:
        st.session_state[f"auth_{slug}"] = False
        st.sidebar.error("❌ كلمة المرور غير صحيحة.")

# ================= Google Drive Setup =================
@st.cache_resource
def get_drive_service():
    try:
        # بناء معلومات حساب الخدمة من الأسرار
        required_keys = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        sa_info = {}
        
        for key in required_keys:
            value = st.secrets.get(key, "")
            if not value:
                raise ValueError(f"المفتاح '{key}' غير موجود في الأسرار")
            sa_info[key] = value
        
        # إضافة المفاتيح الإضافية
        optional_keys = ["client_id", "auth_uri", "token_uri", 
                        "auth_provider_x509_cert_url", "client_x509_cert_url"]
        
        for key in optional_keys:
            value = st.secrets.get(key, "")
            if value:
                sa_info[key] = value
        
        # معالجة private_key
        private_key = sa_info["private_key"].strip()
        if "\\n" in private_key:
            private_key = private_key.replace("\\n", "\n")
        sa_info["private_key"] = private_key
        
        # إنشاء الاعتماد
        creds = service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        
        # بناء الخدمة
        service = build("drive", "v3", credentials=creds)
        
        # اختبار الاتصال
        about = service.about().get(fields="user").execute()
        user_email = about.get("user", {}).get("emailAddress", "غير معروف")
        st.sidebar.success(f"✅ متصل بـ: {user_email}")
        
        return service
    
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال بـ Google Drive: {str(e)}")
        return None

# الاتصال بـ Google Drive
drive_service = get_drive_service()

if not drive_service:
    st.error("""
    ❌ تعذر الاتصال بـ Google Drive
    
    **الخطوات اللازمة:**
    1. أنشئ مفتاح خدمة جديد من Google Cloud Console
    2. انسخ private_key و private_key_id الجديدين
    3. أضف PW_POLICIES = "1234" وغيرها إلى الأسرار
    4. تأكد من مشاركة المجلد مع: ims-storage-service-94@cryptic-woods-445905-f0.iam.gserviceaccount.com
    """)
    st.stop()

# ================= Drive Functions =================
def list_files_in_folder(folder_id: str):
    try:
        q = f"'{folder_id}' in parents and trashed = false"
        res = drive_service.files().list(
            q=q,
            fields="files(id,name,size,modifiedTime)",
            orderBy="modifiedTime desc"
        ).execute()
        return res.get("files", [])
    except Exception as e:
        st.error(f"❌ خطأ في جلب الملفات: {e}")
        return []

def download_file(file_id: str):
    try:
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
        return fh.read()
    except Exception as e:
        st.error(f"❌ خطأ في تنزيل الملف: {e}")
        return b""

def upload_file(folder_id: str, file_obj):
    try:
        # إنشاء اسم فريد للملف
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = file_obj.name
        safe_name = f"{timestamp}_{original_name}"
        
        # رفع الملف
        file_metadata = {
            'name': safe_name,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(
            io.BytesIO(file_obj.getvalue()),
            mimetype=file_obj.type or 'application/octet-stream'
        )
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    except Exception as e:
        st.error(f"❌ خطأ في رفع الملف: {e}")
        return None

def delete_file(file_id: str):
    try:
        drive_service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ خطأ في حذف الملف: {e}")
        return False

# ================= Main Interface =================
st.markdown(f"## قسم: {sec_ar}")

# الحصول على معرف المجلد
folder_id = st.secrets.get("DRIVE_ROOT_FOLDER_ID", "")
if not folder_id:
    st.error("❌ DRIVE_ROOT_FOLDER_ID غير موجود في الأسرار")
    st.stop()

# عرض الملفات
st.markdown("### الملفات الحالية 📂")

if st.button("🔄 تحديث القائمة"):
    st.rerun()

files = list_files_in_folder(folder_id)

if not files:
    st.info("📭 لا توجد ملفات في هذا القسم.")
else:
    for i, file in enumerate(files, 1):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            file_name = file.get('name', 'بدون اسم')
            file_size = file.get('size', 0)
            
            # حساب الحجم بشكل مقروء
            size_str = f"{file_size} B"
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            elif file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            
            st.markdown(f"**{i}. {file_name}** ({size_str})")
        
        with col2:
            file_id = file['id']
            file_content = download_file(file_id)
            
            if file_content:
                st.download_button(
                    label="⬇️ تنزيل",
                    data=file_content,
                    file_name=file_name,
                    key=f"dl_{file_id}"
                )
        
        with col3:
            if st.session_state.get(f"auth_{slug}", False):
                if st.button("🗑️", key=f"del_{file_id}", help="حذف الملف"):
                    if delete_file(file_id):
                        st.success("✅ تم حذف الملف")
                        st.rerun()

# ================= Upload Section =================
st.markdown("### رفع ملف جديد 📤")

if st.session_state.get(f"auth_{slug}", False):
    uploaded_file = st.file_uploader(
        "اختر ملفًا للرفع",
        type=['pdf', 'docx', 'xlsx', 'jpg', 'png', 'txt'],
        key=f"upload_{slug}"
    )
    
    if uploaded_file is not None:
        if st.button("رفع الملف", key=f"upload_btn_{slug}"):
            with st.spinner("جاري رفع الملف..."):
                file_id = upload_file(folder_id, uploaded_file)
                if file_id:
                    st.success("✅ تم رفع الملف بنجاح!")
                    st.rerun()
else:
    st.info("🔒 لرفع أو حذف الملفات، أدخل كلمة المرور الصحيحة في القائمة الجانبية.")

st.markdown("---")
st.markdown(
    "<div class='sig'>تصميم وتطوير رئيس مهندسين أقدم طارق مجيد الكريمي ©</div>",
    unsafe_allow_html=True,
)
