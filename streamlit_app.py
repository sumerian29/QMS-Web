# ------------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ------------------------------------------------------------

import os
import io
import base64
from datetime import datetime
from typing import List, Tuple, Dict

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
  .cert-caption{max-width:980px;margin:4px auto 18px;text-align:center;color:#6b7280;font-size:13px}
</style>
""",
    unsafe_allow_html=True,
)

# ================= Header / Hero =============
CERT_PATH = "iso_cert.jpg"   # صورة شهادة ISO
LOGO_PATH = "sold.png"       # شعار الشركة


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


# ================= Google Drive Setup =================
DRIVE_ROOT_FOLDER_ID = st.secrets.get("DRIVE_ROOT_FOLDER_ID", "").strip()
if not DRIVE_ROOT_FOLDER_ID:
    st.error("⚠️ لم يتم ضبط DRIVE_ROOT_FOLDER_ID في Secrets. يرجى إضافته.")
    st.stop()

SECTION_FOLDER_IDS: Dict[str, str] = dict(st.secrets.get("DRIVE_SECTION_FOLDERS", {}))


@st.cache_resource
def get_drive_service():
    """
    اتصال Google Drive (مهم جدًا: إصلاح private_key إن كان يحتوي \\n).
    """
    sa_info = dict(st.secrets["google_service_account"])

    # ✅ إصلاح مشاكل التنسيق الشائعة في Streamlit Secrets
    pk = sa_info.get("private_key", "")
    if isinstance(pk, str):
        pk = pk.strip()
        # إذا كان موجوداً مثل "\\n" نحوله إلى أسطر حقيقية
        pk = pk.replace("\\n", "\n")
        # إزالة اقتباسات زائدة إن وُجدت
        pk = pk.strip('"').strip("'")
        sa_info["private_key"] = pk

    creds = service_account.Credentials.from_service_account_info(
        sa_info,
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    return build("drive", "v3", credentials=creds)


drive_service = get_drive_service()


@st.cache_data
def human_size(n: int) -> str:
    if n is None:
        return "—"
    n = int(n)
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def auth_key(slug: str) -> str:
    return f"auth_{slug}"


def ensure_section_folder(slug: str) -> str:
    """
    1) إذا أعطيت Folder ID في Secrets نستخدمه مباشرة.
    2) إن لم يوجد، ننشئ/نبحث داخل الجذر كحل احتياطي.
    """
    if slug in SECTION_FOLDER_IDS and SECTION_FOLDER_IDS[slug].strip():
        return SECTION_FOLDER_IDS[slug].strip()

    q = (
        f"'{DRIVE_ROOT_FOLDER_ID}' in parents and "
        f"name = '{slug}' and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )
    res = drive_service.files().list(q=q, fields="files(id,name)", spaces="drive").execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]

    meta = {
        "name": slug,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [DRIVE_ROOT_FOLDER_ID],
    }
    folder = drive_service.files().create(body=meta, fields="id").execute()
    return folder["id"]


def list_files(slug: str) -> List[Tuple[str, int, str, str]]:
    """
    (name, size, file_id, mimeType)
    """
    folder_id = ensure_section_folder(slug)
    q = f"'{folder_id}' in parents and trashed = false"
    res = drive_service.files().list(
        q=q,
        fields="files(id,name,size,mimeType,modifiedTime)",
        orderBy="modifiedTime desc",
        spaces="drive",
    ).execute()

    out = []
    for f in res.get("files", []):
        out.append((
            f.get("name", "file"),
            int(f.get("size", 0) or 0),
            f.get("id", ""),
            f.get("mimeType", ""),
        ))
    return out


def download_file_content(file_id: str, mime_type: str) -> bytes:
    """
    تنزيل:
    - الملفات العادية: get_media
    - Google Docs/Sheets/Slides: export_media (لأن get_media يعطي 403)
    """
    google_types = {
        "application/vnd.google-apps.document": ("application/pdf", ".pdf"),
        "application/vnd.google-apps.spreadsheet": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
        "application/vnd.google-apps.presentation": ("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
    }

    fh = io.BytesIO()

    if mime_type in google_types:
        export_mime, _ = google_types[mime_type]
        request = drive_service.files().export_media(fileId=file_id, mimeType=export_mime)
        downloader = MediaIoBaseDownload(fh, request)
    else:
        request = drive_service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.seek(0)
    return fh.read()


def suggest_download_name(original_name: str, mime_type: str) -> str:
    google_types = {
        "application/vnd.google-apps.document": ".pdf",
        "application/vnd.google-apps.spreadsheet": ".xlsx",
        "application/vnd.google-apps.presentation": ".pptx",
    }
    ext = google_types.get(mime_type)
    if not ext:
        return original_name

    base, _old = os.path.splitext(original_name)
    return f"{base}{ext}"


def save_upload(slug: str, up) -> str:
    try:
        folder_id = ensure_section_folder(slug)

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
        return "__ERROR__:" + str(e)


def delete_file(file_id: str) -> None:
    drive_service.files().delete(fileId=file_id).execute()


# ================= Sidebar: اختيار القسم + كلمة المرور =========
st.sidebar.markdown("### اختر القسم")
sec_ar = st.sidebar.selectbox("اختر", list(SECTIONS_AR2EN.keys()))
slug = SECTIONS_AR2EN[sec_ar]

sec_secret = st.secrets.get(SECRET_KEYS.get(slug, ""), "")

st.sidebar.markdown("### صلاحيات القسم")
pw = st.sidebar.text_input("كلمة المرور (للرفع والحذف فقط)", type="password", key=f"pw_{slug}")

if st.sidebar.button("دخول", key=f"enter_{slug}"):
    if pw and sec_secret and pw.strip() == sec_secret.strip():
        st.session_state[auth_key(slug)] = True
        st.sidebar.success("تم التحقق من كلمة المرور.")
    else:
        st.session_state[auth_key(slug)] = False
        st.sidebar.error("كلمة المرور غير صحيحة.")


# ================= Files (قراءة للجميع) =========
st.markdown("### الملفات الحالية (متاحة للقراءة والتحميل للجميع) 📂")

# زر تحديث آمن بدل rerun القديم
if st.button("تحديث القائمة 🔄"):
    st.rerun()

files = list_files(slug)
if not files:
    st.info("لا توجد ملفات بعد في هذا القسم.")
else:
    for i, (nm, sz, fid, mt) in enumerate(files, start=1):
        c1, c2, c3 = st.columns([5, 2, 1])

        with c1:
            st.markdown(
                f"**#{i} — {nm}**  <span class='muted'>({human_size(sz)})</span>",
                unsafe_allow_html=True,
            )

        with c2:
            try:
                content = download_file_content(fid, mt)
                download_name = suggest_download_name(nm, mt)
                st.download_button(
                    "تنزيل",
                    data=content,
                    file_name=download_name,
                    key=f"dl_{slug}_{i}",
                )
            except Exception as e:
                st.caption(f"تعذّر تنزيل الملف: {e}")

        with c3:
            if st.session_state.get(auth_key(slug), False):
                if st.button("حذف", key=f"rm_{slug}_{i}"):
                    try:
                        delete_file(fid)
                        st.success("تم حذف الملف.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"تعذّر الحذف: {e}")


# ================= Control Panel (رفع فقط) =============
st.markdown("### لوحة التحكم (رفع الملفات للقسم المحدد) 🔒")

if st.session_state.get(auth_key(slug), False):
    st.markdown("#### رفع ملف جديد إلى هذا القسم (Google Drive)")
    up = st.file_uploader("اختر ملفًا (PDF, DOCX, XLSX, PNG, JPG, ...)", type=None, key=f"uploader_{slug}")
    if up is not None:
        res = save_upload(slug, up)
        if isinstance(res, str) and res.startswith("__ERROR__:"):
            st.error("تعذّر حفظ الملف: " + res.replace("__ERROR__:", ""))
        else:
            st.success("✅ تم رفع الملف بنجاح إلى Google Drive.")
            st.rerun()
else:
    st.info("لرفع أو حذف الملفات في هذا القسم، أدخل كلمة المرور الصحيحة من القائمة الجانبية.")

st.markdown("<div class='sig'>تصميم وتطوير رئيس مهندسين أقدم طارق مجيد الكريمي ©</div>", unsafe_allow_html=True)
