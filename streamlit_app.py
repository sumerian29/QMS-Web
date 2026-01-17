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
        return "https://raw.githubusercontent.com/nyxb/placeholder-assets/main/toc-logo.png"

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
    st.markdown(
        "<div class='cert-caption'>نسخة من شهادة الاعتماد — Bureau Veritas — 2025</div>",
        unsafe_allow_html=True,
    )

st.divider()

# ================= Sections & Passwords ======
SECTIONS_AR2EN = {
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

SECRET_KEYS = {
    "policies": "PW_POLICIES",
    "objectives": "PW_OBJECTIVES",
    "docs": "PW_DOCS",
    "audit-plan": "PW_AUDIT",
    "audits": "PW_AUDITS",
    "nc": "PW_NC",
    "capa": "PW_CAPA",
    "kb": "PW_KB",
    "reports": "PW_REPORTS",
    "kpi": "PW_KPI",
    "esign": "PW_ESIGN",
    "notify": "PW_NOTIFY",
    "risks": "PW_RISKS",
}

# ================= Helpers =================
@st.cache_data
def human_size(n: int) -> str:
    n = int(n or 0)
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"

def auth_key(slug: str) -> str:
    return f"auth_{slug}"

def normalize_private_key(raw_key: str) -> str:
    if not raw_key:
        return ""
    
    key = raw_key.strip().strip('"').strip("'")
    
    if "\\n" in key and "\n" not in key:
        key = key.replace("\\n", "\n")
    
    if "BEGIN PRIVATE KEY" not in key:
        key = f"-----BEGIN PRIVATE KEY-----\n{key}\n-----END PRIVATE KEY-----"
    
    key = key.replace("\r\n", "\n").replace("\r", "\n").strip()
    
    return key

def get_section_folder_id_from_secrets(slug: str) -> Optional[str]:
    try:
        # محاولة قراءة من DRIVE_SECTION_FOLDERS أولاً
        if "DRIVE_SECTION_FOLDERS" in st.secrets:
            mapping = st.secrets["DRIVE_SECTION_FOLDERS"]
            if isinstance(mapping, dict):
                val = str(mapping.get(slug, "")).strip()
                if val:
                    return val
        
        # استخدام DRIVE_ROOT_FOLDER_ID كبديل
        root_id = st.secrets.get("DRIVE_ROOT_FOLDER_ID", "").strip()
        if root_id:
            return root_id
        
        return None
    except Exception as e:
        st.warning(f"خطأ في قراءة معرف المجلد: {e}")
        return None

# ================= Sidebar =================
st.sidebar.markdown("### اختر القسم")
sec_ar = st.sidebar.selectbox("اختر", list(SECTIONS_AR2EN.keys()), key="section_select")
slug = SECTIONS_AR2EN[sec_ar]

st.sidebar.markdown("### صلاحيات القسم")

# الحصول على كلمة المرور - الطريقة الصحيحة لقراءة الأسرار
password_key = SECRET_KEYS.get(slug, "")
sec_secret = ""

if password_key:
    # محاولة قراءة كلمة المرور بطرق مختلفة
    try:
        # الطريقة 1: مباشرة من st.secrets
        sec_secret = st.secrets.get(password_key, "")
        
        # الطريقة 2: إذا لم تنجح، جرب قراءة ككائن
        if not sec_secret:
            try:
                all_secrets = dict(st.secrets)
                sec_secret = all_secrets.get(password_key, "")
            except:
                pass
    except Exception as e:
        st.sidebar.error(f"خطأ في قراءة كلمة المرور: {e}")

pw = st.sidebar.text_input(
    "كلمة المرور (للرفع والحذف فقط)",
    type="password",
    key=f"pw_{slug}",
    value=""
)

# زر الدخول
if st.sidebar.button("دخول", key=f"enter_{slug}"):
    if not sec_secret:
        st.sidebar.error(f"❌ كلمة المرور غير مضبوطة. تأكد من وجود {password_key} في الأسرار.")
        
        # عرض جميع المفاتيح المتاحة للمساعدة في التصحيح
        with st.sidebar.expander("المفاتيح المتاحة في الأسرار"):
            try:
                all_keys = []
                for key in st.secrets.keys():
                    all_keys.append(key)
                st.write("المفاتيح العلوية:", all_keys)
                
                # عرض مفاتيح PW_
                pw_keys = [k for k in all_keys if k.startswith('PW_')]
                st.write("مفاتيح كلمات المرور (PW_):", pw_keys)
            except:
                st.write("لا يمكن قراءة المفاتيح")
    
    elif not pw:
        st.sidebar.error("❌ الرجاء إدخال كلمة المرور.")
    
    elif pw.strip() == str(sec_secret).strip():
        st.session_state[auth_key(slug)] = True
        st.sidebar.success("✅ تم التحقق من كلمة المرور.")
        st.rerun()
    
    else:
        st.session_state[auth_key(slug)] = False
        st.sidebar.error("❌ كلمة المرور غير صحيحة.")

# ================= Google Drive Setup =================
@st.cache_resource
def get_drive_service():
    try:
        # قراءة جميع مفاتيح حساب الخدمة
        sa_keys = [
            "type", "project_id", "private_key_id", "private_key",
            "client_email", "client_id", "auth_uri", "token_uri",
            "auth_provider_x509_cert_url", "client_x509_cert_url", "universe_domain"
        ]
        
        sa_info = {}
        for key in sa_keys:
            value = st.secrets.get(key, "")
            if value:
                sa_info[key] = value
        
        # التحقق من المفاتيح الأساسية
        required = ["type", "project_id", "private_key", "client_email"]
        missing = [k for k in required if not sa_info.get(k)]
        
        if missing:
            raise ValueError(f"مفاتيح ناقصة: {missing}")
        
        # إصلاح private_key
        pk = normalize_private_key(sa_info["private_key"])
        if not pk:
            raise ValueError("private_key غير صالح")
        sa_info["private_key"] = pk
        
        # إنشاء الاعتماد
        creds = service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        
        # بناء الخدمة
        service = build("drive", "v3", credentials=creds)
        
        # اختبار الاتصال
        try:
            about = service.about().get(fields="user").execute()
            user_email = about.get("user", {}).get("emailAddress", "غير معروف")
            st.sidebar.success(f"✅ متصل بـ: {user_email}")
        except Exception as test_error:
            st.sidebar.warning(f"⚠️ اختبار الاتصال: {str(test_error)[:100]}")
        
        return service
    
    except Exception as e:
        st.error(f"❌ خطأ في تهيئة Google Drive: {str(e)}")
        st.info("""
        **تأكد من:**
        1. جميع مفاتيح حساب الخدمة موجودة في الأسرار
        2. private_key صحيح ويحتوي على BEGIN/END PRIVATE KEY
        3. تم مشاركة المجلد مع: ims-storage-service-94@cryptic-woods-445905-f0.iam.gserviceaccount.com
        """)
        raise

# محاولة الاتصال بـ Google Drive
drive_service = None
try:
    drive_service = get_drive_service()
    drive_ready = True
except Exception as e:
    drive_ready = False
    st.error(f"❌ فشل الاتصال بـ Google Drive: {str(e)}")
    st.stop()

# ================= Core Drive Functions =================
def list_files_in_folder(folder_id: str) -> List[Tuple[str, int, str, str]]:
    """إرجاع قائمة الملفات مع نوع MIME"""
    if not drive_service or not folder_id:
        return []
    try:
        q = f"'{folder_id}' in parents and trashed = false"
        res = (
            drive_service.files()
            .list(
                q=q,
                fields="files(id,name,size,modifiedTime,mimeType)",
                orderBy="modifiedTime desc",
                spaces="drive",
            )
            .execute()
        )
        items = res.get("files", [])
        out: List[Tuple[str, int, str, str]] = []
        for f in items:
            out.append((
                f.get("name", "file"),
                int(f.get("size", 0) or 0),
                f["id"],
                f.get("mimeType", "application/octet-stream")
            ))
        return out
    except Exception as e:
        st.error(f"❌ خطأ في سرد الملفات: {e}")
        return []

def download_file_content(file_id: str, file_name: str, mime_type: str) -> bytes:
    """تنزيل الملف مع معالجة أنواع الملفات المختلفة"""
    if not drive_service:
        return b""
    
    try:
        # تحديد إذا كان الملف من نوع Google Docs
        is_google_doc = mime_type.startswith('application/vnd.google-apps.')
        
        if is_google_doc:
            # تحديد تنسيق التصدير المناسب
            export_mime = None
            
            if mime_type == 'application/vnd.google-apps.document':
                export_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                file_name = file_name.rsplit('.', 1)[0] + '.docx'
            elif mime_type == 'application/vnd.google-apps.spreadsheet':
                export_mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_name = file_name.rsplit('.', 1)[0] + '.xlsx'
            elif mime_type == 'application/vnd.google-apps.presentation':
                export_mime = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                file_name = file_name.rsplit('.', 1)[0] + '.pptx'
            elif mime_type == 'application/vnd.google-apps.drawing':
                export_mime = 'image/png'
                file_name = file_name.rsplit('.', 1)[0] + '.png'
            elif mime_type == 'application/vnd.google-apps.script':
                export_mime = 'application/vnd.google-apps.script+json'
            else:
                # افتراضي: تصدير كـ PDF
                export_mime = 'application/pdf'
                file_name = file_name.rsplit('.', 1)[0] + '.pdf'
            
            # تصدير ملف Google Docs
            request = drive_service.files().export_media(
                fileId=file_id,
                mimeType=export_mime
            )
        else:
            # تنزيل الملفات العادية
            request = drive_service.files().get_media(fileId=file_id)
        
        # تنزيل المحتوى
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
        return fh.read()
    
    except Exception as e:
        # إذا فشل التصدير، حاول تنزيل الملف بشكل عادي
        if 'is_google_doc' in locals() and is_google_doc:
            try:
                st.warning(f"⚠️ تعذر تصدير ملف Google Docs، جاري تنزيل المعلومات...")
                # إرجاع رسالة توضيحية
                return b"Google Docs file - use browser to open"
            except:
                pass
        
        st.error(f"❌ خطأ في تنزيل الملف: {str(e)[:200]}")
        return b""

def save_upload_to_folder(folder_id: str, up) -> str:
    if not drive_service:
        return ""
    try:
        up.seek(0)
        raw = up.getbuffer() if hasattr(up, "getbuffer") else up.read()
        raw = bytes(raw)

        stamp = datetime.now().strftime("%H%M%S-%Y%m%d")
        base, ext = os.path.splitext(up.name or "file")
        safe = "".join(ch if (ch.isalnum() or ch in ("_", "-", ".", " ")) else "_" for ch in base)
        safe = "_".join(safe.split())
        fname = f"{stamp}_{safe}{ext.lower()}"

        media = MediaIoBaseUpload(
            io.BytesIO(raw),
            mimetype=up.type or "application/octet-stream",
            resumable=False,
        )

        file_meta = {"name": fname, "parents": [folder_id]}
        created = drive_service.files().create(body=file_meta, media_body=media, fields="id").execute()
        return created["id"]
    except Exception as e:
        st.error(f"❌ خطأ في رفع الملف: {e}")
        return ""

def delete_file(file_id: str) -> None:
    if not drive_service:
        return
    try:
        drive_service.files().delete(fileId=file_id).execute()
    except Exception as e:
        st.error(f"❌ خطأ في حذف الملف: {e}")
        raise

# ================= تحديد مجلد القسم =================
folder_id = get_section_folder_id_from_secrets(slug)
if not folder_id:
    st.error(f"""
    ⚠️ لم يتم العثور على Folder ID للقسم '{sec_ar}'
    
    **الحلول:**
    1. تأكد من وجود DRIVE_ROOT_FOLDER_ID في الأسرار
    2. أو أضف [DRIVE_SECTION_FOLDERS] في الأسرار
    """)
    st.stop()

# ================= عرض الملفات =========
st.markdown("### الملفات الحالية (متاحة للقراءة والتحميل للجميع) 📂")

if st.button("🔄 تحديث القائمة", key="refresh_list"):
    st.rerun()

files = list_files_in_folder(folder_id)
if not files:
    st.info("📭 لا توجد ملفات بعد في هذا القسم.")
else:
    for i, (nm, sz, fid, mime_type) in enumerate(files, start=1):
        c1, c2, c3 = st.columns([6, 2, 1])
        
        with c1:
            # أيقونة حسب نوع الملف
            icon = "📄"
            if "google-apps" in mime_type:
                icon = "🌐"
            elif "image" in mime_type:
                icon = "🖼️"
            elif "pdf" in mime_type:
                icon = "📕"
            elif "word" in mime_type:
                icon = "📝"
            elif "excel" in mime_type or "spreadsheet" in mime_type:
                icon = "📊"
            elif "presentation" in mime_type:
                icon = "📽️"
            
            # عرض معلومات الملف
            file_info = f"{icon} **#{i} — {nm}**"
            if sz > 0:
                file_info += f" <span class='muted'>({human_size(sz)})</span>"
            
            # إضافة ملاحظة لملفات Google Docs
            if "google-apps" in mime_type:
                file_info += " <span class='muted'>(Google Docs)</span>"
            
            st.markdown(file_info, unsafe_allow_html=True)
        
        with c2:
            try:
                content = download_file_content(fid, nm, mime_type)
                if content:
                    # تجنب إنشاء زر تنزيل للملفات الفارغة
                    if len(content) > 0 and content != b"Google Docs file - use browser to open":
                        st.download_button(
                            "⬇️ تنزيل",
                            data=content,
                            file_name=nm,
                            mime=mime_type,
                            key=f"dl_{slug}_{i}",
                        )
                    else:
                        st.caption("🔒 غير قابل للتنزيل")
                else:
                    st.caption("❌ فشل التنزيل")
            except Exception as e:
                st.caption(f"⚠️ {str(e)[:50]}")
        
        with c3:
            if st.session_state.get(auth_key(slug), False):
                if st.button("🗑️", key=f"rm_{slug}_{i}", help="حذف الملف"):
                    try:
                        delete_file(fid)
                        st.success("✅ تم حذف الملف.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ تعذّر الحذف: {e}")

# ================= لوحة التحكم =============
st.markdown("### لوحة التحكم (رفع الملفات للقسم المحدد) 🔒")

if st.session_state.get(auth_key(slug), False):
    st.success("✅ أنت مصادق لرفع وحذف الملفات في هذا القسم.")
    
    st.markdown("#### رفع ملف جديد إلى هذا القسم")
    up = st.file_uploader(
        "اختر ملفًا (PDF, DOCX, XLSX, PNG, JPG, ...)",
        type=None,
        key=f"uploader_{slug}",
    )
    
    if up is not None:
        try:
            saved_id = save_upload_to_folder(folder_id, up)
            if saved_id:
                st.success("✅ تم رفع الملف بنجاح إلى Google Drive.")
                st.rerun()
        except Exception as e:
            st.error(f"❌ تعذّر رفع الملف: {e}")
else:
    st.info("🔒 لرفع أو حذف الملفات في هذا القسم، أدخل كلمة المرور الصحيحة من القائمة الجانبية.")

st.markdown(
    "<div class='sig'>تصميم وتطوير رئيس مهندسين أقدم طارق مجيد الكريمي ©</div>",
    unsafe_allow_html=True,
)
