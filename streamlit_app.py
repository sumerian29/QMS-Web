import os
import base64
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st
from github import Github

# -------------------------------
# إعدادات عامة
# -------------------------------
st.set_page_config(page_title="QMS Web — Thi Qar Oil Company", layout="wide")

SECTIONS = {
    "Quality Policy": {"slug": "policies"},
    "Objectives": {"slug": "objectives"},
    "Document Control": {"slug": "documents"},
    "Audit Plan": {"slug": "audit_plan"},
    "Audits": {"slug": "audits"},
    "Non-Conformance": {"slug": "non_conformance"},
    "CAPA": {"slug": "capa"},
    "Knowledge Base": {"slug": "knowledge"},
}

# -------------------------------
# ترويسة مع الشعار
# -------------------------------
col_logo, col_title, col_empty = st.columns([1,3,1])
with col_logo:
    # يعرض الشعار من جذر المستودع (sold.png)
    st.image(os.path.join(os.path.dirname(__file__), "sold.png"), width=110)
with col_title:
    st.markdown(
        """
        <div style="text-align:center;">
          <h2 style="margin-bottom:4px;color:#0b3d6e;">QMS — Quality & Performance Division</h2>
          <h4 style="margin-top:0;color:#ad8c1f;">Thi Qar Oil Company</h4>
          <div style="height:6px;background:linear-gradient(90deg,#0d7a33,#ad8c1f,#0d7a33);border-radius:6px;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------
# الإتصال بـ GitHub (من Secrets)
# -------------------------------
# في Streamlit Cloud > Manage app > Settings > Secrets ضَع:
# [secrets]
# GH_TOKEN = "ghp_xxx..."
# GH_OWNER = "sumerian29"
# GH_REPO  = "QMS-Web"
# PW_POLICIES   = "policy-2025"
# PW_OBJECTIVES = "obj-2025"
# PW_DOCS       = "docs-2025"
# PW_AUDIT      = "audit-2025"
# PW_AUDITS     = "audits-2025"
# PW_NC         = "nc-2025"
# PW_CAPA       = "capa-2025"
# PW_KB         = "kb-2025"
# PW_REPORTS    = "reports-2025"
# PW_KPI        = "kpi-2025"
# PW_ESIGN      = "esign-2025"
# PW_NOTIFY     = "notify-2025"

try:
    GH_TOKEN = st.secrets["GH_TOKEN"]
    GH_OWNER = st.secrets["GH_OWNER"]
    GH_REPO  = st.secrets["GH_REPO"]
except Exception:
    st.error("Secrets GH_TOKEN / GH_OWNER / GH_REPO غير مضبوطة في Streamlit Secrets.")
    st.stop()

gh = Github(GH_TOKEN)
repo = gh.get_user(GH_OWNER).get_repo(GH_REPO)

def gh_list_files(path: str):
    """يجلب قائمة ملفات مجلد ما من المستودع."""
    try:
        contents = repo.get_contents(path)
        files = []
        for c in contents:
            if c.type == "file":
                files.append({
                    "name": c.name,
                    "path": c.path,
                    "sha":  c.sha,
                    "size": c.size,
                    "download_url": c.download_url
                })
        return files
    except Exception:
        return []

def gh_upload_file(path: str, data_bytes: bytes, message: str):
    """يرفع ملف جديد أو يحدّثه إن كان موجوداً."""
    try:
        try:
            existing = repo.get_contents(path)
        except Exception:
            existing = None

        if existing:
            repo.update_file(path, message, data_bytes, existing.sha, branch="main")
        else:
            repo.create_file(path, message, data_bytes, branch="main")
        return True, "Done"
    except Exception as e:
        return False, str(e)

def gh_delete_file(path: str, sha: str, message: str):
    try:
        repo.delete_file(path, message, sha, branch="main")
        return True, "Deleted"
    except Exception as e:
        return False, str(e)

def section_password_ok(section_key: str, entered: str):
    """يتحقق من كلمة مرور القسم من Secrets."""
    try:
        return entered == st.secrets.get(section_key, "")
    except Exception:
        return False

# -------------------------------
# واجهة المستخدم
# -------------------------------
st.sidebar.markdown("### اختر القسم")
sec_names = list(SECTIONS.keys())
selected = st.sidebar.selectbox("اختر القسم", sec_names)
info = SECTIONS[selected]
folder = f"storage/{info['slug']}"   # مجلد التخزين داخل المستودع

st.subheader(selected)

# قائمة الملفات الحالية
files = gh_list_files(folder)

if files:
    df = pd.DataFrame([{"File": f["name"], "Size": f["size"], "Path": f["path"]} for f in files])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("لا توجد ملفات بعد في هذا القسم.")

st.divider()

# وضع القراءة للجميع:
st.markdown("### تنزيل الملفات")
if files:
    for f in files:
        st.markdown(f"- [{f['name']}]({f['download_url']})")
else:
    st.caption("—")

st.divider()

# تحكم الصلاحيات (رفع/حذف) بكلمة مرور القسم
with st.expander("🔐 لوحة التحكم (يتطلب كلمة مرور القسم)"):
    pwd = st.text_input(f"أدخل كلمة مرور قسم [{info['slug']}]", type="password")
    if st.button("Unlock", use_container_width=False):
        if section_password_ok(info["pw_key"], pwd):
            st.success("تم فتح الصلاحيات. يمكنك الرفع/الحذف لهذا القسم.")
            st.session_state[f"unlocked_{info['slug']}"] = True
        else:
            st.error("كلمة المرور غير صحيحة.")

if st.session_state.get(f"unlocked_{info['slug']}", False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### رفع ملف (Excel / Word / PDF / صورة)")
        up = st.file_uploader(
            "اختر ملفاً",
            type=["xlsx","xls","docx","pdf","png","jpg","jpeg"]
        )
        if up is not None:
            safe_name = up.name
            bytes_data = up.read()
            path = f"{folder}/{safe_name}"
            ok, msg = gh_upload_file(
                path,
                bytes_data,
                message=f"[{selected}] upload {safe_name} @ {datetime.now().isoformat(timespec='seconds')}"
            )
            if ok:
                st.success("تم الرفع بنجاح. حدّث الصفحة إذا لم يظهر الملف فوراً.")
            else:
                st.error(f"فشل الرفع: {msg}")

    with col2:
        st.markdown("#### حذف ملف")
        if files:
            to_del = st.selectbox("اختر ملفاً للحذف", [f["name"] for f in files])
            if st.button("حذف الملف المحدد"):
                target = [f for f in files if f["name"] == to_del][0]
                ok, msg = gh_delete_file(
                    target["path"],
                    target["sha"],
                    message=f"[{selected}] delete {to_del} @ {datetime.now().isoformat(timespec='seconds')}"
                )
                if ok:
                    st.success("تم الحذف.")
                else:
                    st.error(f"فشل الحذف: {msg}")
        else:
            st.caption("لا يوجد ما يُحذف.")

# تذييل
st.markdown("<hr/>", unsafe_allow_html=True)
st.caption("© QMS Web — Thi Qar Oil Company — Designed by Chief Engineer Tareq Majeed Al-Karimi")

