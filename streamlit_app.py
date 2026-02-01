# ====================================================
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ====================================================

import os
import io
import base64
import json
import re
from datetime import datetime
from typing import List, Tuple, Dict, Optional

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.errors import HttpError

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
  .error-box {background:#fee;border:1px solid #fcc;border-radius:8px;padding:12px;margin:10px 0;}
  .success-box {background:#dfd;border:1px solid #afa;border-radius:8px;padding:12px;margin:10px 0;}
</style>
""",
    unsafe_allow_html=True,
)

# ================= Header / Hero =============
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

# عرض الهيدر
st.markdown("<div class='hero-wrap'>", unsafe_allow_html=True)
colA, colB, colC = st.columns([1, 3, 1])
with colB:
    logo_src = inline_logo_src(LOGO_PATH)
    if logo_src:
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
    else:
        st.markdown(
            """
            <div class='ttl'>
              <h1>IMS — Integrated Management System</h1>
              <h2>شركة نفط ذي قار</h2>
              <h3>شعبة الجودة وتقويم الأداء المؤسسي</h3>
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

# ================= Sections & Passwords ======
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

# ================= Helper Functions =================
@st.cache_data
def human_size(n: int) -> str:
    """تحويل الحجم إلى صيغة مقروءة"""
    n = int(n or 0)
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

def check_secrets():
    """فحص جميع الأسرار المطلوبة"""
    issues = []

    # فحص وجود google_service_account
    gsa = st.secrets.get("google_service_account", None)
    if not gsa:
        issues.append("❌ القسم 'google_service_account' غير موجود في الأسرار")
    else:
        required_service_keys = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        for key in required_service_keys:
            if key not in gsa or not str(gsa.get(key, "")).strip():
                issues.append(f"❌ {key} غير موجود أو فارغ")

    # فحص DRIVE_ROOT_FOLDER_ID
    if "DRIVE_ROOT_FOLDER_ID" not in st.secrets or not str(st.secrets.get("DRIVE_ROOT_FOLDER_ID", "")).strip():
        issues.append("❌ DRIVE_ROOT_FOLDER_ID غير موجود")

    # فحص كلمات المرور
    password_keys = [f"PW_{key.upper().replace('-', '_')}" for key in SECTIONS.values()]
    missing_passwords = [key for key in password_keys if key not in st.secrets]
    if missing_passwords:
        issues.append(f"❌ {len(missing_passwords)} من مفاتيح كلمات المرور مفقودة")

    # فحص DRIVE_SECTION_FOLDERS
    if "DRIVE_SECTION_FOLDERS" not in st.secrets:
        issues.append("❌ DRIVE_SECTION_FOLDERS غير موجود")
    else:
        try:
            folders_str = st.secrets.get("DRIVE_SECTION_FOLDERS", "{}")
            folders = json.loads(folders_str)
            for section in SECTIONS.values():
                if section not in folders:
                    issues.append(f"❌ المجلد للقسم '{section}' غير موجود في DRIVE_SECTION_FOLDERS")
        except json.JSONDecodeError:
            issues.append("❌ DRIVE_SECTION_FOLDERS ليس بصيغة JSON صحيحة")

    return issues

def auto_fix_secrets():
    """محاولة تصحيح مشاكل الأسرار تلقائياً"""
    fixes = []
    
    # 1. تصحيح مشكلة private_key
    if "google_service_account" in st.secrets:
        gsa = dict(st.secrets["google_service_account"])
        if "private_key" in gsa:
            private_key = gsa["private_key"]
            # إصلاح المشاكل الشائعة في private_key
            if "-----BEGIN PRIVATE KEY-----" not in private_key:
                fixed_key = f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----"
                gsa["private_key"] = fixed_key
                st.secrets["google_service_account"] = gsa
                fixes.append("✅ تم إصلاح private_key (أضيفت العلامات المفقودة)")
    
    # 2. التأكد من أن جميع كلمات المرور موجودة
    required_passwords = [f"PW_{key.upper().replace('-', '_')}" for key in SECTIONS.values()]
    for pw_key in required_passwords:
        if pw_key not in st.secrets:
            # تعيين كلمة مرور افتراضية
            st.secrets[pw_key] = "1234"
            fixes.append(f"✅ تم إضافة {pw_key} بكلمة مرور مؤقتة")
    
    # 3. التأكد من وجود DRIVE_SECTION_FOLDERS كـ JSON
    if "DRIVE_SECTION_FOLDERS" not in st.secrets:
        # إنشاء JSON افتراضي يستخدم المجلد الجذر لجميع الأقسام
        root_folder = st.secrets.get("DRIVE_ROOT_FOLDER_ID", "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ")
        default_folders = {slug: root_folder for slug in SECTIONS.values()}
        st.secrets["DRIVE_SECTION_FOLDERS"] = json.dumps(default_folders, ensure_ascii=False)
        fixes.append("✅ تم إنشاء DRIVE_SECTION_FOLDERS افتراضياً")
    else:
        # التحقق من صحة JSON
        try:
            folders_str = st.secrets.get("DRIVE_SECTION_FOLDERS", "{}")
            json.loads(folders_str)
        except json.JSONDecodeError:
            # إصلاح JSON غير صالح
            root_folder = st.secrets.get("DRIVE_ROOT_FOLDER_ID", "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ")
            default_folders = {slug: root_folder for slug in SECTIONS.values()}
            st.secrets["DRIVE_SECTION_FOLDERS"] = json.dumps(default_folders, ensure_ascii=False)
            fixes.append("✅ تم إصلاح DRIVE_SECTION_FOLDERS (كان JSON غير صالح)")
    
    return fixes

def get_section_folders():
    """تحميل وتفسير DRIVE_SECTION_FOLDERS بشكل صحيح"""
    if "DRIVE_SECTION_FOLDERS" not in st.secrets:
        return {}
    
    folders_str = st.secrets.get("DRIVE_SECTION_FOLDERS", "{}")
    try:
        # إذا كان JSON string
        if isinstance(folders_str, str) and folders_str.strip():
            return json.loads(folders_str)
        # إذا كان dict مباشرة (نادر في Streamlit)
        elif isinstance(folders_str, dict):
            return folders_str
        else:
            return {}
    except json.JSONDecodeError as e:
        st.error(f"❌ خطأ في تحليل JSON لـ DRIVE_SECTION_FOLDERS: {str(e)}")
        return {}
    except Exception as e:
        st.error(f"❌ خطأ غير متوقع في تحليل المجلدات: {str(e)}")
        return {}

def get_section_folder_id(section_slug: str) -> str:
    """الحصول على معرف المجلد الخاص بالقسم بشكل ذكي"""
    # 1. محاولة الحصول من DRIVE_SECTION_FOLDERS
    folders = get_section_folders()
    if section_slug in folders and folders[section_slug] and folders[section_slug] != "REPLACE_WITH_FOLDER_ID":
        return folders[section_slug]
    
    # 2. استخدام المجلد الجذر كبديل
    root_folder = st.secrets.get("DRIVE_ROOT_FOLDER_ID", "")
    if root_folder and root_folder != "REPLACE_WITH_ROOT_FOLDER_ID":
        return root_folder
    
    # 3. إنشاء معرف افتراضي (للأقسام المحددة مسبقاً)
    default_folders = {
        "policies": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "objectives": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "docs": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "audit-plan": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "audits": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "nc": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "capa": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "kb": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "reports": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "kpi": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "esign": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "notify": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
        "risks": "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ",
    }
    return default_folders.get(section_slug, "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ")

def normalize_private_key(key_text: str) -> str:
    """تطبيع وتصحيح تنسيق المفتاح الخاص"""
    if not key_text:
        return ""

    key_text = key_text.strip().strip('"').strip("'")

    # استبدال \n حقيقية
    if "\\n" in key_text and "\n" not in key_text:
        key_text = key_text.replace("\\n", "\n")

    # إضافة البداية والنهاية إذا لم تكن موجودة
    if "-----BEGIN PRIVATE KEY-----" not in key_text:
        key_text = f"-----BEGIN PRIVATE KEY-----\n{key_text}\n-----END PRIVATE KEY-----"

    # تنظيف الأسطر
    lines = key_text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

# ================= Sidebar =================
st.sidebar.markdown("### اختر القسم")
selected_section_ar = st.sidebar.selectbox("اختر", list(SECTIONS.keys()), key="section_select", label_visibility="collapsed")
section_slug = SECTIONS[selected_section_ar]

st.sidebar.markdown("### صلاحيات القسم")

password_key = f"PW_{section_slug.upper().replace('-', '_')}"
section_password = st.secrets.get(password_key, "")

if not section_password:
    st.sidebar.error(f"⚠️ كلمة المرور للقسم غير مضبوطة ({password_key})")
else:
    st.sidebar.success("✅ كلمة المرور للقسم مضبوطة")

password_input = st.sidebar.text_input(
    "كلمة المرور (للرفع والحذف فقط)",
    type="password",
    key=f"pw_{section_slug}",
    value="",
    label_visibility="visible"
)

if st.sidebar.button("دخول", key=f"enter_{section_slug}", use_container_width=True):
    if not section_password:
        st.sidebar.error(f"❌ المفتاح '{password_key}' غير موجود في الأسرار.")
    elif not password_input:
        st.sidebar.error("❌ الرجاء إدخال كلمة المرور.")
    elif password_input.strip() == str(section_password).strip():
        st.session_state[f"auth_{section_slug}"] = True
        st.sidebar.success("✅ تم التحقق من كلمة المرور.")
        st.rerun()
    else:
        st.session_state[f"auth_{section_slug}"] = False
        st.sidebar.error("❌ كلمة المرور غير صحيحة.")

# أزرار الخدمة
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🔍 فحص", key="check_secrets", use_container_width=True):
        issues = check_secrets()
        if issues:
            st.sidebar.error("### مشاكل في الأسرار:")
            for issue in issues:
                st.sidebar.write(issue)
        else:
            st.sidebar.success("✅ جميع الأسرار مضبوطة")

with col2:
    if st.button("🔧 إصلاح", key="auto_fix", use_container_width=True):
        try:
            fixes = auto_fix_secrets()
            if fixes:
                st.sidebar.success("✅ تم الإصلاح:")
                for fix in fixes:
                    st.sidebar.write(f"• {fix}")
                st.rerun()
            else:
                st.sidebar.info("⚠️ لا تحتاج للإصلاح")
        except Exception as e:
            st.sidebar.error(f"❌ فشل الإصلاح: {str(e)}")

# ================= Google Drive Setup =================
@st.cache_resource
def get_drive_service():
    """إنشاء وتوصيل خدمة Google Drive"""
    try:
        if "google_service_account" not in st.secrets:
            raise ValueError("القسم 'google_service_account' غير موجود في الأسرار")

        service_account_info = dict(st.secrets["google_service_account"])
        client_email = service_account_info.get("client_email", "unknown")

        # تطبيع المفتاح الخاص
        if "private_key" in service_account_info:
            service_account_info["private_key"] = normalize_private_key(service_account_info["private_key"])

        private_key = service_account_info.get("private_key", "")
        if not private_key or "-----BEGIN PRIVATE KEY-----" not in private_key:
            st.error("❌ المفتاح الخاص غير صالح - تأكد من وجود '-----BEGIN PRIVATE KEY-----'")
            return None

        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/drive"],
        )

        service = build("drive", "v3", credentials=credentials)

        # اختبار الاتصال
        try:
            about = service.about().get(fields="user").execute()
            st.sidebar.success(f"✅ متصل بـ Google Drive")
            return service
        except Exception as test_error:
            error_msg = str(test_error)
            if "invalid_grant" in error_msg:
                st.sidebar.error("❌ المفتاح الخاص منتهي الصلاحية أو غير صالح")
            elif "access_denied" in error_msg:
                st.sidebar.error("❌ حساب الخدمة ليس لديه صلاحية الوصول")
            else:
                st.sidebar.warning(f"⚠️ اختبار الاتصال: {error_msg[:80]}")
            return service

    except HttpError as http_err:
        error_msg = str(http_err)
        try:
            if hasattr(http_err, "content") and http_err.content:
                error_details = json.loads(http_err.content.decode("utf-8"))
                error_msg = error_details.get("error", {}).get("message", error_msg)
        except Exception:
            pass

        st.error(f"""
        ❌ خطأ في الاتصال بـ Google Drive: {error_msg}

        **الأسباب المحتملة:**
        1. private_key غير صالح (Invalid JWT Signature)
        2. Google Drive API لم يتم تفعيل للمشروع
        3. لم يتم مشاركة المجلد مع حساب الخدمة
        4. انتهت صلاحية المفتاح

        **الحلول المقترحة:**
        1. أنشئ مفتاح خدمة جديد من Google Cloud Console
        2. تأكد من تفعيل Google Drive API للمشروع
        3. تأكد من مشاركة المجلد مع: {client_email}
        4. تأكد من أن DRIVE_ROOT_FOLDER_ID صحيح
        """)
        return None

    except Exception as e:
        st.error(f"""
        ❌ خطأ في الاتصال بـ Google Drive: {str(e)}

        **التحقق من:**
        1. صحة المفتاح الخاص
        2. تفعيل Google Drive API
        3. مشاركة المجلد مع حساب الخدمة
        """)
        return None

drive_service = get_drive_service()

if not drive_service:
    st.error("❌ تعذر الاتصال بـ Google Drive. الرجاء التحقق من الأسرار وإعدادات المشروع.")

    with st.expander("🛠 معلومات التصحيح"):
        st.write("### الأسرار الموجودة:")
        try:
            all_secrets = dict(st.secrets)
            for key, value in all_secrets.items():
                if key == "google_service_account":
                    st.write("**google_service_account:**")
                    gsa = dict(value)
                    for subkey in ["type", "project_id", "client_email"]:
                        if subkey in gsa:
                            st.write(f"  - **{subkey}**: {gsa[subkey]}")
                    if "private_key" in gsa:
                        pk = gsa["private_key"]
                        has_begin = "✅" if "-----BEGIN PRIVATE KEY-----" in pk else "❌"
                        pk_preview = pk[:100] + "..." if len(pk) > 100 else pk
                        st.write(f"  - **private_key**: {has_begin} {len(pk)} حرف - {pk_preview}")
                else:
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    st.write(f"**{key}**: {value_str}")
        except Exception as e:
            st.write(f"لا يمكن قراءة المفاتيح: {str(e)}")

    st.stop()

# ================= Drive Functions =================
def list_files_in_folder(folder_id: str):
    """الحصول على قائمة الملفات في مجلد"""
    if not drive_service or not folder_id:
        return []

    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = drive_service.files().list(
            q=query,
            fields="files(id, name, size, mimeType, modifiedTime, webViewLink, createdTime)",
            orderBy="modifiedTime desc",
            pageSize=100
        ).execute()

        return results.get("files", [])
    except Exception as e:
        st.error(f"❌ خطأ في جلب الملفات: {str(e)[:200]}")
        return []

def download_file_content(file_id: str, file_name: str = None):
    """تنزيل محتوى الملف"""
    if not drive_service:
        return None, None

    try:
        file_info = drive_service.files().get(fileId=file_id, fields="mimeType,name").execute()
        mime_type = file_info.get("mimeType", "")
        original_name = file_info.get("name", file_name or "file")

        if mime_type.startswith("application/vnd.google-apps."):
            export_type = None
            if mime_type == "application/vnd.google-apps.document":
                export_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if not original_name.endswith(".docx"):
                    original_name = f"{original_name}.docx"
            elif mime_type == "application/vnd.google-apps.spreadsheet":
                export_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                if not original_name.endswith(".xlsx"):
                    original_name = f"{original_name}.xlsx"
            elif mime_type == "application/vnd.google-apps.presentation":
                export_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                if not original_name.endswith(".pptx"):
                    original_name = f"{original_name}.pptx"
            else:
                export_type = "application/pdf"
                if not original_name.endswith(".pdf"):
                    original_name = f"{original_name}.pdf"

            request = drive_service.files().export_media(fileId=file_id, mimeType=export_type)
        else:
            request = drive_service.files().get_media(fileId=file_id)

        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        file_handle.seek(0)
        return file_handle.getvalue(), original_name

    except Exception as e:
        st.error(f"❌ خطأ في تنزيل الملف: {str(e)[:200]}")
        return None, None

def upload_file_to_folder(folder_id: str, file_obj):
    """رفع ملف إلى مجلد"""
    if not drive_service:
        return None

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = file_obj.name
        base_name, extension = os.path.splitext(original_name)
        safe_name = f"{timestamp}_{base_name}{extension}"

        file_metadata = {
            "name": safe_name,
            "parents": [folder_id],
            "description": f"تم الرفع من تطبيق IMS - قسم {selected_section_ar}"
        }

        file_handle = io.BytesIO(file_obj.getvalue())
        media = MediaIoBaseUpload(
            file_handle,
            mimetype=file_obj.type or "application/octet-stream",
            resumable=True
        )

        result = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name, webViewLink, mimeType"
        ).execute()

        return result

    except Exception as e:
        st.error(f"❌ خطأ في رفع الملف: {str(e)[:200]}")
        return None

def delete_drive_file(file_id: str):
    """حذف ملف من Google Drive"""
    if not drive_service:
        return False

    try:
        drive_service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ خطأ في حذف الملف: {str(e)[:200]}")
        return False

# ================= Main Interface =================
st.markdown(f"## قسم: {selected_section_ar}")

# الحصول على معرف المجلد الخاص بالقسم
specific_folder_id = get_section_folder_id(section_slug)

# عرض معلومات المجلد
st.caption(f"📁 معرف المجلد: `{specific_folder_id}`")

st.markdown("### الملفات الحالية 📂")

if st.button("🔄 تحديث القائمة", key="refresh_files", use_container_width=True):
    st.rerun()

files = list_files_in_folder(specific_folder_id)

if not files:
    st.info("📭 لا توجد ملفات في هذا القسم.")
    st.markdown("""
    **لرفع ملف جديد:**
    1. أدخل كلمة المرور الصحيحة في الشريط الجانبي
    2. اضغط على زر **"دخول"**
    3. اختر الملف من جهازك
    4. اضغط على **"رفع الملف إلى Google Drive"**
    """)
else:
    for i, file in enumerate(files, 1):
        file_id = file.get("id")
        file_name = file.get("name", "بدون اسم")
        file_size = file.get("size", 0)
        mime_type = file.get("mimeType", "")
        web_link = file.get("webViewLink", "")
        modified_time = file.get("modifiedTime", "")

        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            # اختيار الأيقونة المناسبة
            icon = "📄"
            file_type = "ملف"
            
            if "google-apps" in mime_type:
                icon = "🌐"
                file_type = "ملف Google"
            elif "image" in mime_type:
                icon = "🖼️"
                file_type = "صورة"
            elif "pdf" in mime_type:
                icon = "📕"
                file_type = "PDF"
            elif "document" in mime_type or "word" in mime_type:
                icon = "📝"
                file_type = "مستند"
            elif "spreadsheet" in mime_type or "excel" in mime_type:
                icon = "📊"
                file_type = "جدول بيانات"
            elif "presentation" in mime_type or "powerpoint" in mime_type:
                icon = "📽️"
                file_type = "عرض تقديمي"
            elif "zip" in mime_type or "compressed" in mime_type:
                icon = "📦"
                file_type = "مضغوط"

            st.markdown(f"{icon} **{file_name}**")
            st.caption(f"{file_type} | الحجم: {human_size(file_size)}")
            
            if modified_time:
                try:
                    # تحويل وقت Google إلى تنسيق مقروء
                    dt = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                    st.caption(f"آخر تعديل: {dt.strftime('%Y-%m-%d %H:%M')}")
                except:
                    pass
            
            if web_link:
                st.caption(f"[🔗 فتح في Google Drive]({web_link})")

        with col2:
            if st.button("⬇️ تنزيل", key=f"download_{file_id}_{i}", use_container_width=True):
                with st.spinner("جاري تحضير الملف للتنزيل..."):
                    file_content, download_name = download_file_content(file_id, file_name)
                    if file_content:
                        st.download_button(
                            label="💾 حفظ الملف",
                            data=file_content,
                            file_name=download_name,
                            mime="application/octet-stream",
                            key=f"save_{file_id}_{i}",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ تعذر تحضير الملف للتنزيل")

        with col3:
            if st.session_state.get(f"auth_{section_slug}", False):
                if st.button("🗑️", key=f"delete_{file_id}_{i}", help="حذف الملف", use_container_width=True):
                    # تأكيد الحذف
                    if st.checkbox(f"تأكيد حذف '{file_name}'", key=f"confirm_{file_id}"):
                        if delete_drive_file(file_id):
                            st.success("✅ تم حذف الملف بنجاح")
                            st.rerun()
                        else:
                            st.error("❌ فشل حذف الملف")
            else:
                st.caption("🔒 يتطلب مصادقة")

        if i < len(files):
            st.divider()

# ================= Upload Section =================
st.markdown("---")
st.markdown("### رفع ملف جديد 📤")

if st.session_state.get(f"auth_{section_slug}", False):
    st.success("✅ أنت مصادق لرفع وحذف الملفات في هذا القسم.")

    uploaded_file = st.file_uploader(
        "اختر ملفًا للرفع",
        type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
              'jpg', 'jpeg', 'png', 'txt', 'zip', 'rar', 'csv', 'rtf',
              'mp3', 'mp4', 'wav', 'avi', 'mov'],
        key=f"uploader_{section_slug}"
    )

    if uploaded_file is not None:
        st.write(f"**الملف المحدد:** {uploaded_file.name}")
        st.write(f"**الحجم:** {human_size(uploaded_file.size)}")
        st.write(f"**النوع:** {uploaded_file.type or 'غير معروف'}")

        # إضافة وصف اختياري
        file_description = st.text_area("وصف الملف (اختياري)", key=f"desc_{section_slug}", height=60)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📤 رفع الملف إلى Google Drive", key=f"upload_btn_{section_slug}", use_container_width=True):
                with st.spinner("جاري رفع الملف..."):
                    result = upload_file_to_folder(specific_folder_id, uploaded_file)
                    if result:
                        st.success(f"✅ تم رفع الملف بنجاح: **{result.get('name')}**")
                        if result.get("webViewLink"):
                            st.markdown(f"[🔗 فتح الملف في Drive]({result.get('webViewLink')})")
                        st.rerun()
                    else:
                        st.error("❌ فشل رفع الملف. تحقق من اتصال الإنترنت والصلا
