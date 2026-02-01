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

# ================= Constants =================
DEFAULT_FOLDER_ID = "1q61A-vCir_Vrzo_Qucl8zD02hd9tTKQZ"

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
    if "google_service_account" not in st.secrets:
        issues.append("❌ القسم 'google_service_account' غير موجود في الأسرار")
        return issues  # Return early if no GSA
    
    gsa = st.secrets.get("google_service_account", None)
    if not gsa:
        issues.append("❌ القسم 'google_service_account' موجود لكن فارغ")
        return issues
    
    required_service_keys = ["type", "project_id", "private_key_id", "private_key", "client_email"]
    for key in required_service_keys:
        if key not in gsa:
            issues.append(f"❌ {key} غير موجود في google_service_account")
        else:
            value = gsa.get(key, "")
            if not value or str(value).strip() == "":
                issues.append(f"❌ {key} موجود لكن فارغ")

    # فحص DRIVE_ROOT_FOLDER_ID
    if "DRIVE_ROOT_FOLDER_ID" not in st.secrets:
        issues.append("❌ DRIVE_ROOT_FOLDER_ID غير موجود")
    else:
        root_id = st.secrets.get("DRIVE_ROOT_FOLDER_ID", "")
        if not root_id or str(root_id).strip() == "" or root_id == "REPLACE_WITH_ROOT_FOLDER_ID":
            issues.append("❌ DRIVE_ROOT_FOLDER_ID فارغ أو غير مضبوط")

    # فحص كلمات المرور
    password_keys = [f"PW_{key.upper().replace('-', '_')}" for key in SECTIONS.values()]
    missing_passwords = [key for key in password_keys if key not in st.secrets]
    if missing_passwords:
        issues.append(f"❌ {len(missing_passwords)} من مفاتيح كلمات المرور مفقودة: {', '.join(missing_passwords[:3])}...")

    # فحص DRIVE_SECTION_FOLDERS
    if "DRIVE_SECTION_FOLDERS" not in st.secrets:
        issues.append("❌ DRIVE_SECTION_FOLDERS غير موجود")
    else:
        try:
            folders_str = st.secrets.get("DRIVE_SECTION_FOLDERS", "{}")
            if isinstance(folders_str, str):
                folders_str = folders_str.strip()
            folders = json.loads(folders_str)
            for section in SECTIONS.values():
                if section not in folders:
                    issues.append(f"❌ المجلد للقسم '{section}' غير موجود في DRIVE_SECTION_FOLDERS")
                else:
                    folder_id = folders.get(section, "")
                    if not folder_id or folder_id == "REPLACE_WITH_FOLDER_ID":
                        issues.append(f"❌ معرف المجلد للقسم '{section}' غير مضبوط")
        except json.JSONDecodeError as e:
            issues.append(f"❌ DRIVE_SECTION_FOLDERS ليس بصيغة JSON صحيحة: {str(e)[:100]}")
        except Exception as e:
            issues.append(f"❌ خطأ في تحليل DRIVE_SECTION_FOLDERS: {str(e)[:100]}")

    return issues

def suggest_secrets_fixes():
    """تقديم اقتراحات لإصلاح الأسرار بدون تعديلها"""
    suggestions = []
    issues = check_secrets()
    
    if not issues:
        suggestions.append("✅ جميع الأسرار مضبوطة بشكل صحيح")
        return suggestions
    
    suggestions.append("⚠️ **مشاكل تم اكتشافها:**")
    for issue in issues:
        suggestions.append(f"- {issue}")
    
    suggestions.append("\n🔧 **اقتراحات للإصلاح:**")
    
    # اقتراحات للمفتاح الخاص
    if "google_service_account" in st.secrets:
        gsa = dict(st.secrets["google_service_account"])
        if "private_key" in gsa:
            pk = gsa.get("private_key", "")
            if "-----BEGIN PRIVATE KEY-----" not in pk:
                suggestions.append("1. أضف '-----BEGIN PRIVATE KEY-----' و '-----END PRIVATE KEY-----' إلى private_key")
            if "\\n" in pk and "\n" not in pk:
                suggestions.append("2. استبدل \\n بـ أسطر جديدة حقيقية في private_key")
    
    # اقتراحات للمجلدات
    if "DRIVE_SECTION_FOLDERS" in st.secrets:
        try:
            folders_str = st.secrets.get("DRIVE_SECTION_FOLDERS", "{}")
            folders = json.loads(folders_str)
            missing_sections = [section for section in SECTIONS.values() if section not in folders]
            if missing_sections:
                suggestions.append(f"3. أضف المجلدات المفقودة للأقسام: {', '.join(missing_sections[:3])}...")
        except:
            suggestions.append("3. تأكد أن DRIVE_SECTION_FOLDERS بصيغة JSON صحيحة")
    
    # اقتراحات لكلمات المرور
    password_keys = [f"PW_{key.upper().replace('-', '_')}" for key in SECTIONS.values()]
    missing_passwords = [key for key in password_keys if key not in st.secrets]
    if missing_passwords:
        suggestions.append(f"4. أضف كلمات المرور المفقودة: {', '.join(missing_passwords[:3])}...")
    
    suggestions.append("\n📝 **ملاحظة:** قم بتعديل ملف .streamlit/secrets.toml يدوياً ثم أعد تشغيل التطبيق")
    
    return suggestions

def get_section_folders():
    """تحميل وتفسير DRIVE_SECTION_FOLDERS بشكل صحيح"""
    if "DRIVE_SECTION_FOLDERS" not in st.secrets:
        return {}
    
    folders_str = st.secrets.get("DRIVE_SECTION_FOLDERS", "{}")
    try:
        # تنظيف النص من المسافات الزائدة والأسطر الجديدة
        if isinstance(folders_str, str):
            folders_str = folders_str.strip()
            # إزالة الـ backslashes والمسافات الزائدة
            folders_str = folders_str.replace('\\n', '\n').replace('\\t', '\t')
        
        # محاولة تحميل JSON
        folders = json.loads(folders_str)
        
        # التحقق من أن جميع الأقسام موجودة
        for section in SECTIONS.values():
            if section not in folders:
                st.warning(f"⚠️ قسم '{section}' غير موجود في DRIVE_SECTION_FOLDERS")
                # تعيين معرف افتراضي مؤقت
                folders[section] = st.secrets.get("DRIVE_ROOT_FOLDER_ID", DEFAULT_FOLDER_ID)
        
        return folders
        
    except json.JSONDecodeError as e:
        st.error(f"❌ خطأ في تحليل JSON لـ DRIVE_SECTION_FOLDERS: {str(e)}")
        st.error(f"القيمة المستلمة: {folders_str[:200]}...")
        return {}
    except Exception as e:
        st.error(f"❌ خطأ غير متوقع في تحليل المجلدات: {str(e)}")
        return {}

def get_section_folder_id(section_slug: str) -> str:
    """الحصول على معرف المجلد الخاص بالقسم بشكل ذكي"""
    # 1. محاولة الحصول من DRIVE_SECTION_FOLDERS
    folders = get_section_folders()
    if section_slug in folders and folders[section_slug]:
        folder_id = folders[section_slug]
        if folder_id and folder_id != "REPLACE_WITH_FOLDER_ID":
            return folder_id
    
    # 2. استخدام المجلد الجذر كبديل
    root_folder = st.secrets.get("DRIVE_ROOT_FOLDER_ID", "")
    if root_folder and root_folder != "REPLACE_WITH_ROOT_FOLDER_ID":
        return root_folder
    
    # 3. استخدام المعرف الافتراضي
    return DEFAULT_FOLDER_ID

def normalize_private_key(key_text: str) -> str:
    """تطبيع وتصحيح تنسيق المفتاح الخاص"""
    if not key_text:
        return ""

    key_text = key_text.strip()
    
    # إزالة علامات الاقتباس الزائدة
    key_text = key_text.strip('"').strip("'")
    
    # استبدال \n حقيقية إذا كانت موجودة في النص
    if "\\n" in key_text and "\n" not in key_text:
        key_text = key_text.replace("\\n", "\n")
    
    # إضافة البداية والنهاية إذا لم تكن موجودة
    if "-----BEGIN PRIVATE KEY-----" not in key_text:
        key_text = f"-----BEGIN PRIVATE KEY-----\n{key_text}\n-----END PRIVATE KEY-----"
    
    # تنظيف الأسطر وضمان عدم وجود مسافات زائدة
    lines = key_text.split("\n")
    cleaned_lines = []
    in_key = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line == "-----BEGIN PRIVATE KEY-----":
            in_key = True
            cleaned_lines.append(line)
        elif line == "-----END PRIVATE KEY-----":
            in_key = False
            cleaned_lines.append(line)
        elif in_key:
            # إزالة أي مسافات أو أحرف غير مرغوبة داخل المفتاح
            cleaned_lines.append(line)
    
    return "\n".join(cleaned_lines)

def verify_toml_syntax():
    """فحص صحة بناء TOML والأسرار"""
    results = []
    
    try:
        # Check Google Service Account
        if "google_service_account" not in st.secrets:
            results.append(("❌", "google_service_account غير موجود"))
        else:
            gsa = dict(st.secrets["google_service_account"])
            results.append(("✅", "google_service_account تم تحميله"))
            
            # Check private key format
            pk = gsa.get("private_key", "")
            if "-----BEGIN PRIVATE KEY-----" in pk and "-----END PRIVATE KEY-----" in pk:
                results.append(("✅", "تنسيق private_key صحيح"))
            else:
                results.append(("❌", "private_key يفتقد علامات البداية/النهاية"))
            
            # Check all required keys exist
            required_keys = ["type", "project_id", "private_key_id", "client_email"]
            for key in required_keys:
                if key in gsa and gsa[key]:
                    results.append(("✅", f"{key} موجود"))
                else:
                    results.append(("❌", f"{key} مفقود أو فارغ"))
        
        # Check section folders
        folders = get_section_folders()
        if folders:
            results.append((f"✅", f"تم تحميل {len(folders)} مجلد قسم"))
            for section in SECTIONS.values():
                if section in folders and folders[section]:
                    folder_id = folders[section]
                    if folder_id != "REPLACE_WITH_FOLDER_ID":
                        results.append(("✅", f"مجلد {section} مضبوط"))
                    else:
                        results.append(("⚠️", f"مجلد {section} يحتاج إلى ID حقيقي"))
                else:
                    results.append(("❌", f"مجلد {section} مفقود"))
        else:
            results.append(("❌", "لم يتم تحميل أي مجلدات قسم"))
        
        # Check passwords
        password_keys = [f"PW_{key.upper().replace('-', '_')}" for key in SECTIONS.values()]
        valid_passwords = 0
        for pw_key in password_keys:
            if pw_key in st.secrets and st.secrets[pw_key]:
                valid_passwords += 1
        
        results.append((f"✅" if valid_passwords == len(password_keys) else "⚠️", 
                       f"{valid_passwords}/{len(password_keys)} كلمات مرور مضبوطة"))
        
        return results
        
    except Exception as e:
        results.append(("❌", f"خطأ في فحص TOML: {str(e)[:100]}"))
        return results

# ================= Sidebar =================
st.sidebar.markdown("### اختر القسم")
selected_section_ar = st.sidebar.selectbox("اختر", list(SECTIONS.keys()), key="section_select", label_visibility="collapsed")
section_slug = SECTIONS[selected_section_ar]

st.sidebar.markdown("### صلاحيات القسم")

password_key = f"PW_{section_slug.upper().replace('-', '_')}"
section_password = st.secrets.get(password_key, "")

if not section_password:
    st.sidebar.warning(f"⚠️ كلمة المرور للقسم غير مضبوطة ({password_key})")
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
                st.sidebar.write(f"• {issue}")
        else:
            st.sidebar.success("✅ جميع الأسرار مضبوطة")

with col2:
    if st.button("📝 اقتراحات", key="suggest_fixes", use_container_width=True):
        suggestions = suggest_secrets_fixes()
        with st.sidebar.expander("🔧 اقتراحات الإصلاح", expanded=True):
            for suggestion in suggestions:
                st.write(suggestion)

# زر فحص TOML
if st.sidebar.button("🧪 فحص TOML", key="verify_toml", use_container_width=True):
    results = verify_toml_syntax()
    with st.sidebar.expander("نتائج فحص TOML", expanded=True):
        for status, message in results:
            st.write(f"{status} {message}")

st.sidebar.markdown("---")
st.sidebar.markdown("### معلومات النظام")

# عرض معلومات حساب الخدمة
if "google_service_account" in st.secrets:
    gsa = dict(st.secrets["google_service_account"])
    client_email = gsa.get("client_email", "غير معروف")
    st.sidebar.caption(f"📧 حساب الخدمة: {client_email[:20]}...")

# عرض عدد المجلدات
folders = get_section_folders()
if folders:
    st.sidebar.caption(f"📁 {len(folders)} مجلد قسم")

# ================= Google Drive Setup =================
@st.cache_resource
def get_drive_service():
    """إنشاء وتوصيل خدمة Google Drive"""
    try:
        if "google_service_account" not in st.secrets:
            st.error("❌ القسم 'google_service_account' غير موجود في الأسرار")
            return None

        service_account_info = dict(st.secrets["google_service_account"])
        client_email = service_account_info.get("client_email", "unknown")

        # تطبيع المفتاح الخاص
        if "private_key" in service_account_info:
            service_account_info["private_key"] = normalize_private_key(service_account_info["private_key"])

        private_key = service_account_info.get("private_key", "")
        if not private_key or "-----BEGIN PRIVATE KEY-----" not in private_key:
            st.error("""
            ❌ المفتاح الخاص غير صالح
            **تأكد من:**
            1. وجود '-----BEGIN PRIVATE KEY-----' في البداية
            2. وجود '-----END PRIVATE KEY-----' في النهاية
            3. عدم وجود مسافات زائدة
            """)
            return None

        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/drive"],
        )

        service = build("drive", "v3", credentials=credentials)

        # اختبار الاتصال
        try:
            about = service.about().get(fields="user,storageQuota").execute()
            user_email = about.get("user", {}).get("emailAddress", client_email)
            storage_quota = about.get("storageQuota", {})
            st.sidebar.success(f"✅ متصل بـ Google Drive")
            st.sidebar.caption(f"👤 المستخدم: {user_email}")
            
            # عرض معلومات التخزين إذا كانت متوفرة
            if "limit" in storage_quota and "usage" in storage_quota:
                limit_gb = int(storage_quota["limit"]) / (1024**3) if storage_quota["limit"] != "0" else 0
                usage_gb = int(storage_quota["usage"]) / (1024**3) if storage_quota["usage"] != "0" else 0
                if limit_gb > 0:
                    usage_percent = (usage_gb / limit_gb) * 100
                    st.sidebar.caption(f"💾 التخزين: {usage_gb:.1f}GB / {limit_gb:.1f}GB ({usage_percent:.1f}%)")
            
            return service
        except Exception as test_error:
            error_msg = str(test_error)
            if "invalid_grant" in error_msg.lower():
                st.error("""
                ❌ المفتاح الخاص منتهي الصلاحية أو غير صالح
                **الحل:** أنشئ مفتاح خدمة جديد من Google Cloud Console
                """)
            elif "access_denied" in error_msg.lower():
                st.error(f"""
                ❌ حساب الخدمة ليس لديه صلاحية الوصول
                **الحل:** تأكد من مشاركة المجلدات مع: {client_email}
                """)
            elif "domain" in error_msg.lower() or "not found" in error_msg.lower():
                st.error(f"""
                ❌ المشروع أو الحساب غير موجود
                **الحل:** تأكد من صحة project_id و client_email
                """)
            else:
                st.error(f"⚠️ اختبار الاتصال فشل: {error_msg[:150]}")
            return None

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
        1. private_key غير صالح
        2. Google Drive API لم يتم تفعيل للمشروع
        3. لم يتم مشاركة المجلد مع حساب الخدمة
        4. انتهت صلاحية المفتاح

        **الحلول:**
        1. أنشئ مفتاح خدمة جديد من Google Cloud Console
        2. تفعيل Google Drive API للمشروع
        3. مشاركة المجلدات مع: {client_email}
        4. تأكد من صحة DRIVE_ROOT_FOLDER_ID
        """)
        return None

    except Exception as e:
        st.error(f"""
        ❌ خطأ في الاتصال بـ Google Drive: {str(e)}

        **التحقق من:**
        1. صحة المفتاح الخاص
        2. تفعيل Google Drive API
        3. مشاركة المجلد مع حساب الخدمة
        4. صيغة الأسرار في TOML
        """)
        return None

drive_service = get_drive_service()

if not drive_service:
    st.error("""
    ❌ تعذر الاتصال بـ Google Drive. 
    
    **خطوات التصحيح:**
    1. اضغط على زر "فحص" في الشريط الجانبي
    2. اتبع الاقتراحات الظاهرة
    3. تأكد من صحة المفتاح الخاص
    4. تأكد من مشاركة المجلدات مع حساب الخدمة
    """)

    with st.expander("🛠 معلومات التصحيح المتقدمة"):
        st.write("### الأسرار الموجودة:")
        try:
            all_secrets = dict(st.secrets)
            for key, value in all_secrets.items():
                if key == "google_service_account":
                    st.write("**google_service_account:**")
                    gsa = dict(value)
                    for subkey in ["type", "project_id", "client_email", "private_key_id"]:
                        if subkey in gsa:
                            st.write(f"  - **{subkey}**: {gsa[subkey][:50]}...")
                    if "private_key" in gsa:
                        pk = gsa["private_key"]
                        has_begin = "✅" if "-----BEGIN PRIVATE KEY-----" in pk else "❌"
                        has_end = "✅" if "-----END PRIVATE KEY-----" in pk else "❌"
                        pk_preview = pk[:100] + "..." if len(pk) > 100 else pk
                        st.write(f"  - **private_key**: {has_begin} {has_end} - {len(pk)} حرف")
                        st.code(pk_preview, language="text")
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
            fields="files(id, name, size, mimeType, modifiedTime, webViewLink, createdTime, owners)",
            orderBy="modifiedTime desc",
            pageSize=100
        ).execute()

        files = results.get("files", [])
        
        # تسجيل عدد الملفات المستلمة
        if files:
            st.caption(f"📊 تم تحميل {len(files)} ملف من المجلد")
        
        return files
        
    except Exception as e:
        error_msg = str(e)
        if "notFound" in error_msg:
            st.error(f"❌ المجلد غير موجود أو ليس لديك صلاحية الوصول إليه")
            st.info(f"**معرف المجلد:** {folder_id}")
            st.info("**الحل:** تأكد من مشاركة المجلد مع حساب الخدمة")
        else:
            st.error(f"❌ خطأ في جلب الملفات: {error_msg[:200]}")
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
        
        with st.spinner(f"جاري تنزيل {original_name}..."):
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    st.caption(f"📥 جاري التنزيل: {progress}%")

        file_handle.seek(0)
        return file_handle.getvalue(), original_name

    except Exception as e:
        st.error(f"❌ خطأ في تنزيل الملف: {str(e)[:200]}")
        return None, None

def upload_file_to_folder(folder_id: str, file_obj, description: str = ""):
    """رفع ملف إلى مجلد"""
    if not drive_service:
        return None

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = file_obj.name
        base_name, extension = os.path.splitext(original_name)
        
        # تنظيف اسم الملف من الأحرف غير الآمنة
        safe_base_name = re.sub(r'[^\w\-\.]', '_', base_name)
        safe_name = f"{timestamp}_{safe_base_name}{extension}"

        file_metadata = {
            "name": safe_name,
            "parents": [folder_id],
            "description": description or f"تم الرفع من تطبيق IMS - قسم {selected_section_ar} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }

        file_handle = io.BytesIO(file_obj.getvalue())
        media = MediaIoBaseUpload(
            file_handle,
            mimetype=file_obj.type or "application/octet-stream",
            resumable=True
        )

        with st.spinner(f"جاري رفع {original_name}..."):
            result = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, name, webViewLink, mimeType, size"
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
        with st.spinner("جاري حذف الملف..."):
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
with st.expander("📂 معلومات المجلد", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("معرف المجلد", specific_folder_id[:20] + "...")
    with col2:
        st.metric("القسم", section_slug)
    with col3:
        st.metric("الحالة", "✅ متصل" if drive_service else "❌ غير متصل")
    
    # زر فتح المجلد في Drive
    folder_link = f"https://drive.google.com/drive/folders/{specific_folder_id}"
    st.markdown(f"[🔗 فتح المجلد في Google Drive]({folder_link})")

st.markdown("### الملفات الحالية 📂")

# زر التحديث
if st.button("🔄 تحديث قائمة الملفات", key="refresh_files", use_container_width=True):
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
    
    **ملاحظة:** تأكد من مشاركة المجلد مع حساب الخدمة
    """)
    
    # عرض معلومات المجلد للتصحيح
    with st.expander("🔧 معلومات تصحيح للمجلد"):
        st.code(f"""
        معرف المجلد: {specific_folder_id}
        حساب الخدمة: {st.secrets.get('google_service_account', {}).get('client_email', 'غير معروف')}
        رابط المجلد: https://drive.google.com/drive/folders/{specific_folder_id}
        """)
else:
    # إحصائيات الملفات
    total_size = sum(int(f.get("size", 0)) for f in files)
    st.caption(f"📊 إجمالي {len(files)} ملف | الحجم الإجمالي: {human_size(total_size)}")
    
    for i, file in enumerate(files, 1):
        file_id = file.get("id")
        file_name = file.get("name", "بدون اسم")
        file_size = file.get("size", 0)
        mime_type = file.get("mimeType", "")
        web_link = file.get("webViewLink", "")
        modified_time = file.get("modifiedTime", "")
        created_time = file.get("createdTime", "")

        col1, col2, col3 = st.columns([5, 1, 1])

        with col1:
            # اختيار الأيقونة المناسبة
            icon = "📄"
            file_type = "ملف"
            
            if "google-apps.folder" in mime_type:
                icon = "📁"
                file_type = "مجلد"
            elif "google-apps.document" in mime_type:
                icon = "📝"
                file_type = "مستند Google"
            elif "google-apps.spreadsheet" in mime_type:
                icon = "📊"
                file_type = "جدول بيانات Google"
            elif "google-apps.presentation" in mime_type:
                icon = "📽️"
                file_type = "عرض تقديمي Google"
            elif "google-apps" in mime_type:
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
            elif "audio" in mime_type:
                icon = "🎵"
                file_type = "صوت"
            elif "video" in mime_type:
                icon = "🎬"
                file_type = "فيديو"

            st.markdown(f"{icon} **{file_name}**")
            
            col_info1, col_info2 = st.columns([2, 2])
            with col_info1:
                st.caption(f"{file_type}")
                st.caption(f"الحجم: {human_size(file_size)}")
            
            with col_info2:
                if modified_time:
                    try:
                        dt = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                        st.caption(f"آخر تعديل: {dt.strftime('%Y-%m-%d')}")
                    except:
                        pass
            
            if web_link:
                st.caption(f"[🔗 فتح في Google Drive]({web_link})")

        with col2:
            download_key = f"download_{file_id}_{i}_{section_slug}"
            if st.button("⬇️", key=download_key, help="تنزيل الملف", use_container_width=True):
                with st.spinner("جاري تحضير الملف للتنزيل..."):
                    file_content, download_name = download_file_content(file_id, file_name)
                    if file_content:
                        st.download_button(
                            label="💾 حفظ الملف",
                            data=file_content,
                            file_name=download_name,
                            mime="application/octet-stream",
                            key=f"save_{file_id}_{i}_{section_slug}",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ تعذر تحضير الملف للتنزيل")

        with col3:
            if st.session_state.get(f"auth_{section_slug}", False):
                delete_key = f"delete_{file_id}_{i}_{section_slug}"
                if st.button("🗑️", key=delete_key, help="حذف الملف", use_container_width=True):
                    # تأكيد الحذف مع زرين
                    st.warning(f"⚠️ هل أنت متأكد من حذف '{file_name}'؟")
                    col_confirm1, col_confirm2 = st.columns(2)
                    with col_confirm1:
                        if st.button("✅ نعم، احذفه", key=f"yes_delete_{file_id}"):
                            if delete_drive_file(file_id):
                                st.success("✅ تم حذف الملف بنجاح")
                                st.rerun()
                            else:
                                st.error("❌ فشل حذف الملف")
                    with col_confirm2:
                        if st.button("❌ لا، إلغاء", key=f"no_delete_{file_id}"):
                            st.info("تم إلغاء الحذف")
            else:
                st.caption("🔒 يتطلب مصادقة")

        if i < len(files):
            st.divider()

# ================= Upload Section =================
st.markdown("---")
st.markdown("### رفع ملف جديد 📤")

auth_status = st.session_state.get(f"auth_{section_slug}", False)

if auth_status:
    st.success("✅ أنت مصادق لرفع وحذف الملفات في هذا القسم.")

    uploaded_file = st.file_uploader(
        "اختر ملفًا للرفع",
        type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
              'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg',
              'txt', 'csv', 'json', 'xml', 'rtf',
              'zip', 'rar', '7z', 'tar', 'gz',
              'mp3', 'wav', 'ogg', 'flac',
              'mp4', 'avi', 'mov', 'wmv', 'flv',
              'html', 'htm', 'css', 'js', 'py'],
        key=f"uploader_{section_slug}"
    )

    if uploaded_file is not None:
        st.write(f"**الملف المحدد:** {uploaded_file.name}")
        st.write(f"**الحجم:** {human_size(uploaded_file.size)}")
        st.write(f"**النوع:** {uploaded_file.type or 'غير معروف'}")

        # إضافة وصف اختياري
        file_description = st.text_area(
            "وصف الملف (اختياري)", 
            key=f"desc_{section_slug}", 
            height=60,
            placeholder="أدخل وصفًا للملف (سيظهر في تفاصيل الملف في Google Drive)"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📤 رفع الملف إلى Google Drive", key=f"upload_btn_{section_slug}", use_container_width=True):
                if uploaded_file.size > 100 * 1024 * 1024:  # 100MB limit
                    st.error("❌ حجم الملف كبير جداً (الحد الأقصى 100MB)")
                else:
                    with st.spinner("جاري رفع الملف..."):
                        result = upload_file_to_folder(specific_folder_id, uploaded_file, file_description)
                        if result:
                            file_name = result.get('name', 'الملف')
                            file_size = result.get('size', 0)
                            file_link = result.get('webViewLink', '')
                            
                            st.success(f"✅ تم رفع الملف بنجاح")
                            st.markdown(f"""
                            **تفاصيل الرفع:**
                            - الاسم: **{file_name}**
                            - الحجم: **{human_size(file_size)}**
                            - الوقت: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
                            """)
                            
                            if file_link:
                                st.markdown(f"[🔗 فتح الملف في Drive]({file_link})")
                            
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ فشل رفع الملف. تحقق من اتصال الإنترنت والصلاحيات.")
        
        with col2:
            if st.button("🗑️ مسح التحديد", key=f"clear_{section_slug}", use_container_width=True):
                st.rerun()
else:
    st.warning("""
    ⚠️ **يجب المصادقة للرفع والحذف**
    
    للوصول إلى صلاحيات الرفع والحذف:
    1. أدخل كلمة المرور في الشريط الجانبي
    2. اضغط على زر **"دخول"**
    3. تأكد من ظهور ✅ تحت خانة كلمة المرور
    """)
    
    # عرض معلومات المساعدة
    with st.expander("🆘 مساعدة في المصادقة"):
        st.markdown("""
        **إذا لم تظهر كلمة المرور:**
        1. تأكد من وجود المفتاح `PW_{SECTION}` في ملف secrets.toml
        2. تأكد من إعادة تشغيل التطبيق بعد إضافة المفاتيح
        3. تحقق من صيغة TOML باستخدام زر "فحص TOML"
        
        **مثال لمفتاح كلمة المرور:**
        ```toml
        PW_POLICIES = "1719"
        ```
        
        **حسابات الاختبار:**
        - قسم **سياسة الجودة**: كلمة المرور موجودة في `PW_POLICIES`
        - قسم **الأهداف**: كلمة المرور موجودة في `PW_OBJECTIVES`
        - وهكذا لباقي الأقسام
        """)

# ================= Footer =================
st.markdown("---")
st.markdown(
    """
    <div class='sig'>
    تم التطوير بواسطة شعبة الجودة وتقويم الأداء المؤسسي — شركة نفط ذي قار<br>
    Chief Engineer Tareq Majeed Al-Karimi © 2024
    </div>
    """,
    unsafe_allow_html=True,
)

# Debug information in sidebar
if st.sidebar.checkbox("🔍 عرض معلومات التصحيح", False):
    st.sidebar.markdown("### معلومات التصحيح")
    st.sidebar.json({
        "section_slug": section_slug,
        "folder_id": specific_folder_id,
        "authenticated": auth_status,
        "total_files": len(files),
        "session_keys": [k for k in st.session_state.keys() if k.startswith('auth_')]
    })
