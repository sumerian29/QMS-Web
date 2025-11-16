# ------------------------------------------------------------
# IMS — Integrated Management System (Arabic UI)
# Thi Qar Oil Company — Quality & Institutional Performance Division
# Designed & Developed by Chief Engineer Tareq Majeed Al-Karimi
# ------------------------------------------------------------

import os
import base64
from datetime import datetime
from typing import List, Tuple

import requests
import streamlit as st

# ================= App setup =================
st.set_page_config(page_title="IMS — Thi Qar Oil Company", layout="wide")

# ================= GitHub Config =============

# يجب ضبط هذه القيم في Streamlit secrets
GH_TOKEN = st.secrets.get("GH_TOKEN", "")
GH_OWNER = st.secrets.get("GH_OWNER", "")
GH_REPO  = st.secrets.get("GH_REPO", "")

# فرع الريبو (غالباً main) ومسار الجذر للملفات داخل الريبو
GH_BRANCH    = st.secrets.get("GH_BRANCH", "main")
GH_BASE_PATH = st.secrets.get("GH_BASE_PATH", "qms")

if not GH_TOKEN or not GH_OWNER or not GH_REPO:
    st.error("⚠️ لم يتم ضبط GH_TOKEN / GH_OWNER / GH_REPO في Streamlit Secrets.")
    st.stop()


def github_headers():
    return {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def github_contents_url(path: str) -> str:
    # path مثل "qms/policies/public"
    return f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}"


# دالة تعطي مسار المجلد داخل الريبو حسب القسم ونوع الملفات
def section_folder(slug: str, visibility: str) -> str:
    # visibility = "public" أو "private"
    return f"{GH_BASE_PATH}/{slug}/{visibility}"


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
         border:1px solid #e9eef5; background:#fff;}
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
    وإلا يحاول جلبه من GitHub (raw),
    وإلا يسقط إلى صورة بديلة عامة.
    """
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    except Exception:
        # محاولة جلبه من الريبو نفسه لو مرفوع هناك
        return f"https://raw.githubusercontent.com/{GH_OWNER}/{GH_REPO}/{GH_BRANCH}/{path}"


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

VISIBILITY_LABELS_PUBLIC_ONLY = {
    "الملفات العامة (لجميع الموظفين)": "public",
}
VISIBILITY_LABELS_FULL = {
    "الملفات العامة (لجميع الموظفين)": "public",
    "الملفات الداخلية (الخاصة بمسؤول القسم)": "private",
}


def human_size(n: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def auth_key(slug: str) -> str:
    return f"auth_{slug}"


# ============ GitHub-based storage functions ============

def list_files(slug: str, visibility: str) -> List[Tuple[str, int, str, str, str]]:
    """
    تعيد قائمة ملفات القسم من GitHub:
    (اسم الملف، الحجم، رابط التحميل download_url، المسار path، رقم sha)
    حسب نوع الملفات (public / private).
    """
    folder = section_folder(slug, visibility)
    url = github_contents_url(folder)

    resp = requests.get(url, headers=github_headers())
    if resp.status_code != 200:
        # لو لم يوجد المجلد أصلاً نرجع قائمة فارغة
        return []

    items = resp.json()
    out: List[Tuple[str, int, str, str, str]] = []

    # GitHub يعيد ملفات ومجلدات؛ نأخذ الملفات فقط
    for it in items:
        if it.get("type") == "file":
            name = it["name"]
            size = it.get("size", 0)
            download_url = it.get("download_url")
            path = it.get("path")
            sha = it.get("sha")
            out.append((name, size, download_url, path, sha))

    out.sort(key=lambda x: x[0], reverse=True)
    return out


def delete_file_from_github(path: str, sha: str) -> bool:
    """
    حذف ملف من GitHub بشكل نهائي باستخدام المسار و sha.
    """
    url = github_contents_url(path)
    data = {
        "message": f"Delete {path} via IMS",
        "sha": sha,
        "branch": GH_BRANCH,
    }
    resp = requests.delete(url, headers=github_headers(), json=data)
    return resp.status_code in (200, 204)


def save_upload(slug: str, visibility: str, up):
    """
    حفظ الملف المرفوع داخل مجلد القسم في GitHub (public أو private).
    ينشئ المجلدات تلقائيًا إذا لم تكن موجودة.
    ويمنع تكرار نفس اسم الملف (بعد الجزء الزمني) داخل نفس نوع الملفات.
    """
    try:
        up.seek(0)
        raw = up.getbuffer() if hasattr(up, "getbuffer") else up.read()
        raw = bytes(raw)

        base, ext = os.path.splitext(up.name or "file")
        safe = "".join(
            ch if (ch.isalnum() or ch in ("_", "-", ".", " ")) else "_" for ch in base
        )
        safe = "_".join(safe.split())
        ext = ext.lower()

        folder = section_folder(slug, visibility)
        target_rest = safe + ext  # الاسم الأصلي + الامتداد

        # --- فحص وجود ملف بنفس الاسم في هذا القسم ونفس نوع الملفات مسبقاً ---
        folder_url = github_contents_url(folder)
        resp = requests.get(folder_url, headers=github_headers())
        if resp.status_code == 200:
            items = resp.json()
            for it in items:
                if it.get("type") == "file":
                    existing_name = it["name"]
                    # نأخذ الجزء بعد أول "_" لأنه يأتي بعد التوقيت
                    if "_" in existing_name:
                        existing_rest = existing_name.split("_", 1)[1]
                    else:
                        existing_rest = existing_name
                    if existing_rest == target_rest:
                        # الملف موجود مسبقاً بنفس الاسم
                        return "__DUPLICATE__"

        # --- إنشاء اسم جديد مع ختم زمني ثم الرفع إلى GitHub ---
        stamp = datetime.now().strftime("%H%M%S-%Y%m%d")
        fname = f"{stamp}_{safe}{ext}"
        repo_path = f"{folder}/{fname}"

        content_b64 = base64.b64encode(raw).decode("utf-8")

        url = github_contents_url(repo_path)
        data = {
            "message": f"Add {fname} to {slug}/{visibility} via IMS",
            "content": content_b64,
            "branch": GH_BRANCH,
        }

        resp = requests.put(url, json=data, headers=github_headers())
        if resp.status_code in (201, 200):
            return repo_path
        else:
            return "__ERROR__:" + f"GitHub {resp.status_code}: {resp.text}"

    except Exception as e:
        return "__ERROR__:" + str(e)


# ================= Sidebar: اختيار القسم + كلمة المرور =========

st.sidebar.markdown("### اختر القسم")
sec_ar = st.sidebar.selectbox("اختر", list(SECTIONS_AR2EN.keys()))
slug = SECTIONS_AR2EN[sec_ar]
sec_secret = st.secrets.get(SECRET_KEYS.get(slug, ""), "")

st.sidebar.markdown("### صلاحيات القسم")
pw = st.sidebar.text_input(
    "كلمة المرور (للرفع والملفات الداخلية)",
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

# اختيار نوع الملفات (عام / داخلي)
if st.session_state.get(auth_key(slug), False):
    vis_label = st.sidebar.radio(
        "نوع الملفات المعروضة",
        list(VISIBILITY_LABELS_FULL.keys()),
        key=f"vis_{slug}",
    )
    visibility = VISIBILITY_LABELS_FULL[vis_label]
else:
    vis_label = "الملفات العامة (لجميع الموظفين)"
    visibility = "public"
    st.sidebar.markdown(
        "<span style='font-size:12px;color:#6b7280'>لرؤية الملفات الداخلية ورفعها، أدخل كلمة المرور أعلاه.</span>",
        unsafe_allow_html=True,
    )

# ================= Files (قراءة للجميع أو للخاص) =========

title_suffix = "العامة" if visibility == "public" else "الداخلية (الخاصة)"
st.markdown(f"### الملفات الحالية — {title_suffix} (متاحة للقراءة والتحميل حسب الصلاحيات) 📂")

files = list_files(slug, visibility)
if not files:
    st.info("لا توجد ملفات بعد في هذا القسم لهذا النوع من الملفات.")
else:
    for i, (nm, sz, download_url, path, sha) in enumerate(files, start=1):
        c1, c2, c3 = st.columns([5, 2, 1])
        with c1:
            st.markdown(
                f"**#{i} — {nm}**  <span class='muted'>({human_size(sz)})</span>",
                unsafe_allow_html=True,
            )
        with c2:
            if download_url:
                try:
                    r = requests.get(download_url)
                    if r.status_code == 200:
                        st.download_button(
                            "تنزيل",
                            data=r.content,
                            file_name=nm,
                            key=f"dl_{slug}_{visibility}_{i}",
                        )
                    else:
                        st.caption("تعذّر تحميل الملف من GitHub.")
                except Exception as e:
                    st.caption(f"تعذّر تحميل الملف: {e}")
            else:
                st.caption("لا يوجد رابط تحميل متاح.")
        with c3:
            # الحذف متاح فقط لمن يملك كلمة المرور
            if st.session_state.get(auth_key(slug), False):
                if st.button("حذف", key=f"del_{slug}_{visibility}_{i}"):
                    ok = delete_file_from_github(path, sha)
                    if ok:
                        st.success("✅ تم حذف الملف من GitHub.")
                        st.rerun()
                    else:
                        st.error("تعذّر حذف الملف من GitHub.")

# ================= Control Panel (رفع فقط) =============

st.markdown("### لوحة التحكم (رفع الملفات للقسم المحدد) 🔒")

if st.session_state.get(auth_key(slug), False):
    st.markdown(
        f"#### رفع ملف جديد إلى هذا القسم — نوع الملفات: {'عام' if visibility=='public' else 'داخلي'} (GitHub)"
    )
    up = st.file_uploader(
        "اختر ملفًا (PDF, DOCX, XLSX, PNG, JPG, ...)", type=None, key=f"upl_{slug}_{visibility}"
    )
    if up is not None:
        res = save_upload(slug, visibility, up)
        if res == "__DUPLICATE__":
            st.warning(
                "تم تجاهل الرفع: هذا الملف موجود مسبقًا في هذا القسم بنفس الاسم لهذا النوع من الملفات. "
                "يرجى تغيير اسم الملف أو حذف النسخة القديمة أولاً."
            )
        elif isinstance(res, str) and res.startswith("__ERROR__:"):
            st.error("تعذّر حفظ الملف: " + res.replace("__ERROR__:", ""))
        else:
            st.success("✅ تم رفع الملف بنجاح إلى GitHub.")
            st.rerun()
else:
    st.info("لرفع الملفات العامة أو الداخلية في هذا القسم، أدخل كلمة المرور الصحيحة من القائمة الجانبية.")

st.markdown(
    "<div class='sig'>تصميم وتطوير رئيس مهندسين أقدم طارق مجيد الكريمي ©</div>",
    unsafe_allow_html=True,
)
