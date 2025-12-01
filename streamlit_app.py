# ------------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ------------------------------------------------------------

import os
import io
import base64
from datetime import datetime
from typing import List, Tuple

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

CERT_PATH = "iso_cert.jpg"   # ضع الصورة بهذا الاسم بجانب الملف لعرض شهادة ISO
LOGO_PATH = "sold.png"       # شعار الشركة محليًا باسم sold.png


@st.cache_data
def inline_logo_src(path: str = "sold.png") -> str:
    """
    يعيد Data URI للصورة من الملف المحلي إن وجد،
    وإلا يسقط إلى صورة بديلة عامة.
    """
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
    st.image(CERT_PATH, use_column_width=True)
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


@st.cache_resource
def get_drive_service():
    """إنشاء اتصال واحد فقط بـ Google Drive."""
    sa_info = dict(st.secrets["google_service_account"])
    creds = service_account.Credentials.from_service_account_info(
        sa_info,
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    service = build("drive", "v3", credentials=creds)
    return service


drive_service = get_drive_service()


@st.cache_data
def human_size(n: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def auth_key(slug: str) -> str:
    return f"auth_{slug}"


# حفظ ID مجلدات الأقسام في الذاكرة
if "section_folders" not in st.session_state:
    st.session_state["section_folders"] = {}


def ensure_section_folder(slug: str) -> str:
    """
    يتحقق من وجود مجلد داخل IMS-Storage للقسم، وإن لم يوجد ينشئه.
    اسم المجلد هو نفس slug (policies, objectives, ...).
    """
    cache = st.session_state["section_folders"]
    if slug in cache:
        return cache[slug]

    # البحث عن المجلد بالاسم داخل الجذر
    q = (
        f"'{DRIVE_ROOT_FOLDER_ID}' in parents and "
        f"name = '{slug}' and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )
    res = (
        drive_service.files()
        .list(q=q, fields="files(id,name)", spaces="drive")
        .execute()
    )
    files = res.get("files", [])
    if files:
        folder_id = files[0]["id"]
    else:
        # إنشاء مجلد جديد
        meta = {
            "name": slug,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [DRIVE_ROOT_FOLDER_ID],
        }
        folder = drive_service.files().create(body=meta, fields="id").execute()
        folder_id = folder["id"]

    cache[slug] = folder_id
    return folder_id


def list_files(slug: str) -> List[Tuple[str, int, str]]:
    """
    يرجع قائمة ملفات القسم من Google Drive:
    (الاسم، الحجم، file_id)
    """
    folder_id = ensure_section_folder(slug)

    q = f"'{folder_id}' in parents and trashed = false"
    res = (
        drive_service.files()
        .list(
            q=q,
            fields="files(id, name, size, modifiedTime)",
            orderBy="name desc",
        )
        .execute()
    )
    items = res.get("files", [])
    out: List[Tuple[str, int, str]] = []
    for f in items:
        name = f.get("name", "file")
        size = int(f.get("size", 0))
        fid = f.get("id")
        out.append((name, size, fid))
    # مرتبة تنازلياً بالاسم (مثل السابق)
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def download_file_content(file_id: str) -> bytes:
    """تحميل محتوى ملف من Google Drive لاستخدامه في download_button."""
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return fh.read()


def save_upload(slug: str, up) -> str:
    """
    رفع ملف جديد إلى مجلد القسم في Google Drive.
    يعيد file_id أو رسالة خطأ تبدأ بـ __ERROR__.
    """
    try:
        folder_id = ensure_section_folder(slug)
        up.seek(0)
        raw = up.getbuffer() if hasattr(up, "getbuffer") else up.read()
        raw = bytes(raw)

        stamp = datetime.now().strftime("%H%M%S-%Y%m%d")
        base, ext = os.path.splitext(up.name or "file")
        safe = "".join(
            ch if (ch.isalnum() or ch in ("_", "-", ".", " ")) else "_" for ch in base
        )
        safe = "_".join(safe.split())
        fname = f"{stamp}_{safe}{ext.lower()}"

        media = MediaIoBaseUpload(
            io.BytesIO(raw),
            mimetype=up.type or "application/octet-stream",
            resumable=False,
        )

        file_meta = {"name": fname, "parents": [folder_id]}
        created = (
            drive_service.files()
            .create(body=file_meta, media_body=media, fields="id")
            .execute()
        )
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
pw = st.sidebar.text_input(
    "كلمة المرور (للرفع والحذف فقط)",
    type="password",
    key=f"pw_{slug}",
)
if st.sidebar.button("دخول", key=f"enter_{slug}"):
    if pw and sec_secret and pw.strip() == sec_secret.strip():
        st.session_state[auth_key(slug)] = True
        st.sidebar.success("تم التحقق من كلمة المرور.")
    else:
        st.session_state[auth_key(slug)] = False
        st.sidebar.error("كلمة المرور غير صحيحة.")

# ================= Files (قراءة للجميع) =========

st.markdown("### الملفات الحالية (متاحة للقراءة والتحميل للجميع) 📂")

files = list_files(slug)
if not files:
    st.info("لا توجد ملفات بعد في هذا القسم.")
else:
    for i, (nm, sz, fid) in enumerate(files, start=1):
        c1, c2, c3 = st.columns([5, 2, 1])
        with c1:
            st.markdown(
                f"**#{i} — {nm}**  <span class='muted'>({human_size(sz)})</span>",
                unsafe_allow_html=True,
            )
        with c2:
            try:
                content = download_file_content(fid)
                st.download_button(
                    "تنزيل",
                    data=content,
                    file_name=nm,
                    key=f"dl_{slug}_{i}",
                )
            except Exception as e:
                st.caption(f"تعذّر تنزيل الملف: {e}")
        with c3:
            # زر حذف يظهر فقط لو المستخدم أدخل كلمة المرور
            if st.session_state.get(auth_key(slug), False):
                if st.button("حذف", key=f"rm_{slug}_{i}"):
                    try:
                        delete_file(fid)
                        st.success("تم حذف الملف.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"تعذّر الحذف: {e}")

# ================= Control Panel (رفع فقط) =============

st.markdown("### لوحة التحكم (رفع الملفات للقسم المحدد) 🔒")

if st.session_state.get(auth_key(slug), False):
    st.markdown("#### رفع ملف جديد إلى هذا القسم (Google Drive)")
    up = st.file_uploader(
        "اختر ملفًا (PDF, DOCX, XLSX, PNG, JPG, ...)", type=None, key=f"uploader_{slug}"
    )
    if up is not None:
        res = save_upload(slug, up)
        if isinstance(res, str) and res.startswith("__ERROR__:"):
            st.error("تعذّر حفظ الملف: " + res.replace("__ERROR__:", ""))
        else:
            st.success("✅ تم رفع الملف بنجاح إلى Google Drive.")
            st.experimental_rerun()
else:
    st.info("لرفع أو حذف الملفات في هذا القسم، أدخل كلمة المرور الصحيحة من القائمة الجانبية.")

st.markdown(
    "<div class='sig'>تصميم وتطوير رئيس مهندسين أقدم طارق مجيد الكريمي ©</div>",
    unsafe_allow_html=True,
)
