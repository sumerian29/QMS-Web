# ------------------------------------------------------------
# IMS / File Console (Arabic UI) — with Trash & Restore
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ------------------------------------------------------------

import os
import io
import hashlib
from datetime import datetime
from typing import List, Tuple
import streamlit as st

# ==========================
# إعداد عام
# ==========================
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

st.markdown("""
<style>
  body, .stApp { background-color:#f3f7fb; }
  .hero { background:#0b4a6f0d; border-radius:14px; padding:10px 16px; margin:6px 0 20px; 
          border:1px solid #e7eef6; font-weight:600; text-align:center;}
  .gold { background:linear-gradient(90deg,#b8860b,#cda434,#b8860b); color:#13233a;
          padding:10px 16px; border-radius:12px; font-weight:700; }
  .code-note { color:#6b7280; font-size:12px; }
  .card { background:white; border:1px solid #eaeef4; border-radius:14px; padding:12px 14px; }
  .muted { color:#6b7280; font-size:13px; }
  .sig { text-align:center; color:#a07a00; font-weight:700; margin-top:10px;}
  .center { text-align:center; }
</style>
""", unsafe_allow_html=True)

# ==========================
# الأقسام + كلمات المرور (من Secrets)
# ==========================
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

# جذر التخزين
BASE_DIR = os.path.join(os.getcwd(), "uploads")
TRASH_ROOT = os.path.join(BASE_DIR, ".trash")


# ==========================
# دوال مساعدة
# ==========================
def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def section_dir(slug: str) -> str:
    p = os.path.join(BASE_DIR, slug)
    ensure_dir(p)
    return p

def human_size(n: int) -> str:
    for unit in ["B","KB","MB","GB"]:
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def list_files(slug: str) -> List[Tuple[str, int, str]]:
    root = section_dir(slug)
    files = []
    for nm in os.listdir(root):
        path = os.path.join(root, nm)
        if os.path.isfile(path):
            files.append((nm, os.path.getsize(path), path))
    files.sort(key=lambda x: x[0], reverse=True)
    return files

def auth_state_key(slug: str) -> str:
    return f"auth_{slug}"

def save_upload(slug: str, up_file) -> str:
    root = section_dir(slug)
    raw = up_file.read()
    digest = sha256_bytes(raw)

    for nm in os.listdir(root):
        p = os.path.join(root, nm)
        if p.endswith(".sha") or not os.path.isfile(p):
            continue
        sha_path = p + ".sha"
        if os.path.exists(sha_path):
            try:
                with open(sha_path, "r", encoding="utf-8") as fh:
                    if fh.read().strip() == digest:
                        return ""  # مكرر
            except:
                pass

    stamp = datetime.now().strftime("%H%M%S-%Y%m%d")
    base, ext = os.path.splitext(up_file.name)
    safe_base = base.replace("/", "_").replace("\\", "_").replace(" ", "_")
    fname = f"{stamp}_{safe_base}{ext}"
    fpath = os.path.join(root, fname)

    with open(fpath, "wb") as fh:
        fh.write(raw)

    with open(fpath + ".sha", "w", encoding="utf-8") as fh:
        fh.write(digest)
    return fpath

def move_to_trash(slug: str, src_path: str) -> str:
    ensure_dir(TRASH_ROOT)
    trash_sec = os.path.join(TRASH_ROOT, slug)
    ensure_dir(trash_sec)
    base = os.path.basename(src_path)
    name, ext = os.path.splitext(base)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(trash_sec, f"{name}__DELETED__{stamp}{ext}")
    os.replace(src_path, dst)
    sha_src = src_path + ".sha"
    if os.path.exists(sha_src):
        os.replace(sha_src, dst + ".sha")
    return dst

def list_trash(slug: str) -> List[Tuple[str, int, str]]:
    tdir = os.path.join(TRASH_ROOT, slug)
    if not os.path.isdir(tdir):
        return []
    files = []
    for nm in os.listdir(tdir):
        p = os.path.join(tdir, nm)
        if os.path.isfile(p) and not nm.endswith(".sha"):
            files.append((nm, os.path.getsize(p), p))
    files.sort(key=lambda x: x[0], reverse=True)
    return files

def restore_from_trash(slug: str, trash_path: str) -> str:
    root = section_dir(slug)
    base = os.path.basename(trash_path)
    name, ext = os.path.splitext(base)
    original = name.split("__DELETED__")[0] + ext
    dst = os.path.join(root, original)

    if os.path.exists(dst):
        stamp = datetime.now().strftime("%H%M%S-%Y%m%d")
        dst = os.path.join(root, f"{original[:-len(ext)]}__RESTORED__{stamp}{ext}")

    os.replace(trash_path, dst)
    sha_src = trash_path + ".sha"
    if os.path.exists(sha_src):
        os.replace(sha_src, dst + ".sha")
    return dst

def delete_forever(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    sha = path + ".sha"
    if os.path.exists(sha):
        try:
            os.remove(sha)
        except FileNotFoundError:
            pass


# ==========================
# واجهة البداية
# ==========================
colL, colC, colR = st.columns([1,2,1])
with colC:
    st.markdown("<div class='hero gold'>Quality Management System — UKAS Accredited</div>", unsafe_allow_html=True)
    st.markdown("<div class='center'><h3>إنجاز وطني لشركة نفط ذي قار</h3></div>", unsafe_allow_html=True)
    st.markdown(
        """<div class='card center'>
        يُعَد حصول شركة نفط ذي قار على شهادة الاعتماد الدولي <b>ISO 9001:2015</b> من مؤسسة <b>Bureau Veritas</b>
        إنجازًا وطنيًا واستراتيجيًا، تحقق بفضل الجهود الكبيرة لشعبة الجودة وتقويم الأداء المؤسسي في ترسيخ أنظمة الإدارة المتكاملة
        وتطبيق مفاهيم التحسين المستمر وتعزيز ثقافة الجودة في جميع تشكيلات الشركة، دعمًا لمسيرتها نحو التميز والشفافية والالتزام بأعلى المعايير العالمية.
        </div>""",
        unsafe_allow_html=True
    )

st.divider()

# ==========================
# اختيار القسم
# ==========================
st.sidebar.markdown("### اختر القسم")
sec_ar = st.sidebar.selectbox("اختر", list(SECTIONS_AR2EN.keys()))
section_slug = SECTIONS_AR2EN[sec_ar]
sec_key = SECRET_KEYS.get(section_slug, "")
section_password = st.secrets.get(sec_key, "") if sec_key else ""


# ==========================
# عرض الملفات الحالية
# ==========================
st.markdown("### الملفات الحالية (قراءة فقط) 🔐")
files = list_files(section_slug)
if not files:
    st.info("لا توجد ملفات بعد في هذا القسم.")
else:
    for idx, (name, size, path) in enumerate(files, start=1):
        c1, c2, c3 = st.columns([4,1,1])
        with c1:
            st.markdown(f"**#{idx} — {name}**  <span class='code-note'>({human_size(size)})</span>", unsafe_allow_html=True)
        with c2:
            with open(path, "rb") as fh:
                st.download_button("تنزيل", data=fh.read(), file_name=name, type="secondary", key=f"dl_{section_slug}_{idx}")
        with c3:
            if st.session_state.get(auth_state_key(section_slug), False):
                if st.button("حذف", type="primary", key=f"rm_{section_slug}_{idx}"):
                    st.warning(f"سيتم نقل الملف **{name}** إلى سلة المحذوفات.")
                    if st.button(f"تأكيد حذف #{idx}", key=f"rm_cf_{section_slug}_{idx}"):
                        move_to_trash(section_slug, path)
                        st.success("تم نقل الملف إلى سلة المحذوفات.")
                        st.rerun()

# ==========================
# لوحة التحكم
# ==========================
st.markdown("### لوحة التحكم (تتطلب كلمة مرور القسم) 🔒")

pw_col, btn_col = st.columns([3,1])
entered = pw_col.text_input("أدخل كلمة المرور", type="password", placeholder="مثال: policy-2025")
login = btn_col.button("دخول")

if login:
    if entered and section_password and entered.strip() == section_password.strip():
        st.session_state[auth_state_key(section_slug)] = True
        st.success("تم الدخول بنجاح.")
    else:
        st.error("كلمة المرور غير صحيحة.")

if st.session_state.get(auth_state_key(section_slug), False):

    st.markdown("#### رفع ملف إلى هذا القسم")
    up = st.file_uploader("اختر ملفًا (PDF, DOCX, XLSX, PNG, JPG, ...)", type=None)
    if up is not None:
        saved = save_upload(section_slug, up)
        if saved == "":
            st.warning("تم تجاهل الرفع: الملف مكرر تمامًا.")
        else:
            st.success("تم الحفظ بنجاح.")
            st.rerun()

    cur_files = list_files(section_slug)
    if cur_files:
        st.markdown("#### حذف جماعي (نقل إلى سلة المحذوفات)")
        sel = st.multiselect(
            "اختر الملفات:",
            options=[f"#{idx} — {nm}" for idx, (nm, _, _) in enumerate(cur_files, start=1)],
        )
        if st.button("حذف الملفات المحددة"):
            if not sel:
                st.info("لم يتم اختيار أي ملف.")
            else:
                idx_to_path = {i+1: p for i, (_, _, p) in enumerate(cur_files)}
                removed = 0
                for token in sel:
                    num = int(token.split("—")[0].strip().lstrip("#"))
                    move_to_trash(section_slug, idx_to_path[num])
                    removed += 1
                st.success(f"تم نقل {removed} ملف/ملفات إلى سلة المحذوفات.")
                st.rerun()

    with st.expander("🗑️ إدارة سلة المحذوفات لهذا القسم"):
        trash_files = list_trash(section_slug)
        if not trash_files:
            st.info("سلة المحذوفات فارغة.")
        else:
            for idx, (name, size, path) in enumerate(trash_files, start=1):
                c1, c2, c3 = st.columns([4,1,1])
                with c1:
                    st.markdown(f"**#{idx} — {name}**  <span class='code-note'>({human_size(size)})</span>", unsafe_allow_html=True)
                with c2:
                    if st.button("استرجاع", key=f"restore_{section_slug}_{idx}"):
                        restore_from_trash(section_slug, path)
                        st.success("تم الاسترجاع.")
                        st.rerun()
                with c3:
                    if st.button("حذف نهائي", key=f"purge_{section_slug}_{idx}"):
                        delete_forever(path)
                        st.success("تم الحذف النهائي.")
                        st.rerun()
else:
    st.info("أدخل كلمة المرور ثم اضغط (دخول) للوصول إلى أدوات الرفع والحذف.")

st.markdown("<div class='sig'>تصميم وتطوير رئيس مهندسين أقدم طارق مجيد الكريمي ©</div>", unsafe_allow_html=True)
