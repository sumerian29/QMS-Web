# ------------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ------------------------------------------------------------

import os
import base64
import hashlib
from datetime import datetime
from typing import List, Tuple

import streamlit as st

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
    وإلا يحاول جلبه من GitHub Secrets إن وُضعت (GH_OWNER/GH_REPO),
    وإلا يسقط إلى صورة بديلة عامة.
    """
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    except Exception:
        gh_owner = st.secrets.get("GH_OWNER", "")
        gh_repo  = st.secrets.get("GH_REPO", "")
        if gh_owner and gh_repo:
            return f"https://raw.githubusercontent.com/{gh_owner}/{gh_repo}/main/{path}"
        return "https://raw.githubusercontent.com/nyxb/placeholder-assets/main/toc-logo.png"

st.markdown("<div class='hero-wrap'>", unsafe_allow_html=True)
colA, colB, colC = st.columns([1, 3, 1])
with colB:
    # ملاحظة: نعرض الشعار من الملف المحلي sold.png
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

BASE_DIR   = os.path.join(os.getcwd(), "uploads")
TRASH_ROOT = os.path.join(BASE_DIR, ".trash")

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def section_dir(slug: str) -> str:
    p = os.path.join(BASE_DIR, slug)
    ensure_dir(p)
    return p

def human_size(n: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def list_files(slug: str) -> List[Tuple[str, int, str]]:
    root = section_dir(slug)
    out: List[Tuple[str, int, str]] = []
    for nm in os.listdir(root):
        p = os.path.join(root, nm)
        if os.path.isfile(p) and not nm.endswith(".sha"):
            out.append((nm, os.path.getsize(p), p))
    out.sort(key=lambda x: x[0], reverse=True)
    return out

def auth_key(slug: str) -> str:
    return f"auth_{slug}"

# ---------- حفظ الرفع مع منع التكرار ورسائل واضحة ----------
def save_upload(slug: str, up):
    ensure_dir(section_dir(slug))
    try:
        up.seek(0)
        raw = up.getbuffer() if hasattr(up, "getbuffer") else up.read()
        raw = bytes(raw)
        digest = sha256_bytes(raw)

        root = section_dir(slug)
        for nm in os.listdir(root):
            p = os.path.join(root, nm)
            if os.path.isfile(p) and not nm.endswith(".sha"):
                sp = p + ".sha"
                if os.path.exists(sp):
                    try:
                        if open(sp, "r", encoding="utf-8").read().strip() == digest:
                            return ""  # مكرر
                    except Exception:
                        pass

        stamp = datetime.now().strftime("%H%M%S-%Y%m%d")
        base, ext = os.path.splitext(up.name or "file")
        safe = "".join(
            ch if (ch.isalnum() or ch in ("_", "-", ".", " ")) else "_" for ch in base
        )
        safe = "_".join(safe.split())
        fname = f"{stamp}_{safe}{ext.lower()}"
        fpath = os.path.join(root, fname)

        with open(fpath, "wb") as f:
            f.write(raw)
        with open(fpath + ".sha", "w", encoding="utf-8") as f:
            f.write(digest)
        return fpath

    except Exception as e:
        return f"__ERROR__:{e}"

def move_to_trash(slug: str, src: str) -> str:
    ensure_dir(TRASH_ROOT)
    tdir = os.path.join(TRASH_ROOT, slug)
    ensure_dir(tdir)
    base = os.path.basename(src)
    name, ext = os.path.splitext(base)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(tdir, f"{name}__DELETED__{stamp}{ext}")
    os.replace(src, dst)
    if os.path.exists(src + ".sha"):
        os.replace(src + ".sha", dst + ".sha")
    return dst

def list_trash(slug: str) -> List[Tuple[str, int, str]]:
    tdir = os.path.join(TRASH_ROOT, slug)
    if not os.path.isdir(tdir):
        return []
    out: List[Tuple[str, int, str]] = []
    for nm in os.listdir(tdir):
        p = os.path.join(tdir, nm)
        if os.path.isfile(p) and not nm.endswith(".sha"):
            out.append((nm, os.path.getsize(p), p))
    out.sort(key=lambda x: x[0], reverse=True)
    return out

def restore_from_trash(slug: str, tpath: str) -> str:
    root = section_dir(slug)
    base = os.path.basename(tpath)
    name, ext = os.path.splitext(base)
    original = name.split("__DELETED__")[0] + ext
    dst = os.path.join(root, original)
    if os.path.exists(dst):
        stamp = datetime.now().strftime("%H%M%S-%Y%m%d")
        dst = os.path.join(root, f"{original[:-len(ext)]}__RESTORED__{stamp}{ext}")
    os.replace(tpath, dst)
    if os.path.exists(tpath + ".sha"):
        os.replace(tpath + ".sha", dst + ".sha")
    return dst

def delete_forever(p: str):
    try:
        os.remove(p)
    except FileNotFoundError:
        pass
    try:
        os.remove(p + ".sha")
    except FileNotFoundError:
        pass

# ================= Sidebar ===================
st.sidebar.markdown("### اختر القسم")
sec_ar = st.sidebar.selectbox("اختر", list(SECTIONS_AR2EN.keys()))
slug = SECTIONS_AR2EN[sec_ar]
sec_secret = st.secrets.get(SECRET_KEYS.get(slug, ""), "")

# ================= Files (read-only) =========
st.markdown("### الملفات الحالية (قراءة فقط) 🔐")
files = list_files(slug)
if not files:
    st.info("لا توجد ملفات بعد في هذا القسم.")
else:
    for i, (nm, sz, pth) in enumerate(files, start=1):
        c1, c2, c3 = st.columns([4, 1, 1])
        with c1:
            st.markdown(
                f"**#{i} — {nm}**  <span class='muted'>({human_size(sz)})</span>",
                unsafe_allow_html=True,
            )
        with c2:
            # ✅ زر تنزيل صحيح لملف محلي
            try:
                with open(pth, "rb") as fh:
                    st.download_button(
                        "تنزيل",
                        data=fh.read(),
                        file_name=nm,
                        key=f"dl_{slug}_{i}",
                    )
            except Exception as e:
                st.caption(f"تعذّر فتح الملف للتنزيل: {e}")
        with c3:
            if st.session_state.get(auth_key(slug), False):
                if st.button("حذف", key=f"rm_{slug}_{i}"):
                    try:
                        move_to_trash(slug, pth)
                        st.success("تم نقل الملف إلى سلة المحذوفات.")
                        st.rerun(); st.stop()
                    except Exception as e:
                        st.error(f"تعذر الحذف: {e}")

# ================= Control Panel =============
st.markdown("### لوحة التحكم (تتطلب كلمة مرور القسم) 🔒")
c_pw, c_btn = st.columns([3, 1])
pw = c_pw.text_input("أدخل كلمة المرور", type="password", placeholder="مثال: policy-2025")
if c_btn.button("دخول"):
    if pw and sec_secret and pw.strip() == sec_secret.strip():
        st.session_state[auth_key(slug)] = True
        st.success("تم الدخول بنجاح.")
    else:
        st.error("كلمة المرور غير صحيحة.")

if st.session_state.get(auth_key(slug), False):
    st.markdown("#### رفع ملف إلى هذا القسم")
    up = st.file_uploader(
        "اختر ملفًا (PDF, DOCX, XLSX, PNG, JPG, ...)", type=None
    )
    if up is not None:
        res = save_upload(slug, up)
        if res == "":
            st.warning("تم تجاهل الرفع: هذا الملف موجود مسبقًا (مكرر).")
        elif isinstance(res, str) and res.startswith("__ERROR__:"):
            st.error("تعذّر حفظ الملف: " + res.replace("__ERROR__:", ""))
        else:
            st.success("تم الحفظ بنجاح.")
            st.rerun(); st.stop()

    cur = list_files(slug)
    if cur:
        st.markdown("#### حذف جماعي (نقل إلى سلة المحذوفات)")
        labels = [f"#{i} — {nm}" for i, (nm, _, _) in enumerate(cur, start=1)]
        label_to_path = {labels[i]: cur[i][2] for i in range(len(cur))}
        chosen = st.multiselect("اختر الملفات:", options=labels)
        if st.button("حذف الملفات المحددة"):
            if not chosen:
                st.info("لم يتم اختيار أي ملف.")
            else:
                cnt = 0
                for lbl in chosen:
                    p = label_to_path.get(lbl)
                    if p and os.path.exists(p):
                        move_to_trash(slug, p)
                        cnt += 1
                st.success(f"تم نقل {cnt} ملف/ملفات إلى سلة المحذوفات.")
                st.rerun(); st.stop()

    with st.expander("🗑️ إدارة سلة المحذوفات لهذا القسم"):
        trash = list_trash(slug)
        if not trash:
            st.info("سلة المحذوفات فارغة.")
        else:
            for i, (nm, sz, pth) in enumerate(trash, start=1):
                c1, c2, c3 = st.columns([4, 1, 1])
                with c1:
                    st.markdown(
                        f"**#{i} — {nm}**  <span class='muted'>({human_size(sz)})</span>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("استرجاع", key=f"restore_{slug}_{i}"):
                        restore_from_trash(slug, pth)
                        st.success("تم الاسترجاع.")
                        st.rerun(); st.stop()
                with c3:
                    if st.button("حذف نهائي", key=f"purge_{slug}_{i}"):
                        delete_forever(pth)
                        st.success("تم الحذف النهائي.")
                        st.rerun(); st.stop()
else:
    st.info("أدخل كلمة المرور ثم اضغط (دخول) للوصول إلى أدوات الرفع والحذف.")

st.markdown(
    "<div class='sig'>تصميم وتطوير رئيس مهندسين أقدم طارق مجيد الكريمي ©</div>",
    unsafe_allow_html=True,
)
