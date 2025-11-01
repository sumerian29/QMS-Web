import streamlit as st
from github import Github
from io import BytesIO
import base64
import pandas as pd
from datetime import datetime

# -------------------------------
# إعدادات عامة
# -------------------------------
st.set_page_config(page_title="QMS Web — Thi Qar Oil Company", layout="wide")

SECTIONS = {
    "Quality Policy":        {"slug": "policies",   "pw_key": "PW_POLICIES"},
    "Objectives":            {"slug": "objectives", "pw_key": "PW_OBJECTIVES"},
    "Document Control":      {"slug": "docs",       "pw_key": "PW_DOCS"},
    "Audit Plan":            {"slug": "audit",      "pw_key": "PW_AUDIT"},
    "Audits":                {"slug": "audits",     "pw_key": "PW_AUDITS"},
    "Non-Conformance":       {"slug": "nc",         "pw_key": "PW_NC"},
    "CAPA":                  {"slug": "capa",       "pw_key": "PW_CAPA"},
    "Knowledge Base":        {"slug": "kb",         "pw_key": "PW_KB"},
    "Reports":               {"slug": "reports",    "pw_key": "PW_REPORTS"},
    "Performance Eval (KPI)":{"slug": "kpi",        "pw_key": "PW_KPI"},
    "E-Signature":           {"slug": "esign",      "pw_key": "PW_ESIGN"},
    "Notifications":         {"slug": "notify",     "pw_key": "PW_NOTIFY"},
}

# -------------------------------
# الإتصال بـ GitHub
# -------------------------------
# يجب ضبط هذه القيم في Streamlit -> Settings -> Secrets
# [secrets]
# GH_TOKEN="ghp_xxx..."
# GH_OWNER="sumerian29"
# GH_REPO="QMS-Web"
# (وكلمات المرور لكل قسم كما بالأسفل)

try:
    GH_TOKEN = st.secrets["GH_TOKEN"]
    GH_OWNER = st.secrets["GH_OWNER"]
    GH_REPO  = st.secrets["GH_REPO"]
except Exception as e:
    st.error("Secrets GH_TOKEN / GH_OWNER / GH_REPO غير مضبوطة.")
    st.stop()

gh = Github(GH_TOKEN)
repo = gh.get_user(GH_OWNER).get_repo(GH_REPO)

def gh_list_files(path):
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

def gh_upload_file(path, data_bytes, message):
    """يرفع ملف جديد أو يحدّثه إن كان موجوداً."""
    try:
        # هل الملف موجود؟
        existing = None
        try:
            existing = repo.get_contents(path)
        except Exception:
            existing = None

        if existing:
            repo.update_file(path, message, data_bytes, existing.sha, branch="main")
        else:
            # الإنشاء يتطلب تحديد المسار الكامل، مع التأكد من وجود المجلدات
            # GitHub API ينشئ المجلدات تلقائياً إن لم تكن موجودة.
            repo.create_file(path, message, data_bytes, branch="main")
        return True, "Done"
    except Exception as e:
        return False, str(e)

def gh_delete_file(path, sha, message):
    try:
        repo.delete_file(path, message, sha, branch="main")
        return True, "Deleted"
    except Exception as e:
        return False, str(e)

def section_password_ok(section_key, entered):
    """يتحقق من كلمة مرور القسم من Secrets."""
    try:
        return entered == st.secrets.get(section_key, "")
    except Exception:
        return False

# -------------------------------
# واجهة المستخدم
# -------------------------------
st.markdown(
    """
    <h2 style="margin-bottom:0">QMS — Quality & Performance Division | Thi Qar Oil Company</h2>
    <small>Designed by Chief Engineer Tareq Majeed Al-Karimi</small>
    <hr/>
    """,
    unsafe_allow_html=True
)

sec_names = list(SECTIONS.keys())
selected = st.sidebar.selectbox("اختر القسم", sec_names)
info = SECTIONS[selected]
folder = f"storage/{info['slug']}"   # مجلد التخزين داخل المستودع
st.subheader(selected)

# قائمة الملفات الحالية
files = gh_list_files(folder)
if files:
    df = pd.DataFrame([{"File": f["name"], "Size": f["size"], "Path": f["path"]} for f in files])
    st.dataframe(df, use_container_width=True)
else:
    st.info("لا توجد ملفات بعد في هذا القسم.")

st.divider()

# وضع القراءة للجميع:
st.markdown("### تنزيل الملفات")
if files:
    for f in files:
        st.markdown(f"- [{f['name']}]({f['download_url']})")
else:
    st.write("—")

st.divider()

# تحكم الصلاحيات (رفع/حذف) بكلمة مرور القسم
with st.expander("🔐 لوحة التحكم (يتطلب كلمة مرور القسم)"):
    pwd = st.text_input(f"أدخل كلمة مرور قسم [{info['slug']}]", type="password")
    if st.button("Unlock"):
        if section_password_ok(info["pw_key"], pwd):
            st.success("تم فتح الصلاحيات. يمكنك الرفع/الحذف لهذا القسم.")
            st.session_state[f"unlocked_{info['slug']}"] = True
        else:
            st.error("كلمة المرور غير صحيحة.")

if st.session_state.get(f"unlocked_{info['slug']}", False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### رفع ملف (Excel / Word / PDF / صورة)")
        up = st.file_uploader("اختر ملفاً", type=["xlsx","xls","docx","pdf","png","jpg","jpeg"])
        if up:
            # اسم ملف مميز مع التاريخ
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
            st.write("لا يوجد ما يُحذف.")

# تذييل
st.markdown("<hr/>", unsafe_allow_html=True)
st.caption("© QMS Web — Thi Qar Oil Company")
