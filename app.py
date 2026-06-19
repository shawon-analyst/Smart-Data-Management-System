import io
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import db
import auth

# ──────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Data Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

# ──────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* NOTE: We intentionally do NOT hide the header anymore — the sidebar
   collapse/expand arrow lives inside it. Hiding header made the sidebar
   unrecoverable once collapsed. We just make the header transparent
   and remove its default background instead, keeping the toggle visible. */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3rem;
}
header[data-testid="stHeader"] * {
    visibility: visible !important;
}

/* Make sure the sidebar collapse/expand control is always clickable and visible */
button[data-testid="stSidebarCollapseButton"],
button[data-testid="stBaseButton-headerNoPadding"],
div[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
    display: flex !important;
}

/* ---------- Animated gradient title ---------- */
.main-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(270deg, #20c997, #0dcaf0, #845ef7, #20c997);
    background-size: 600% 600%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 10s ease infinite;
    margin-bottom: 0px;
}
.main-subtitle {
    color: #7d8a98;
    font-size: 15px;
    margin-top: -8px;
    margin-bottom: 18px;
}
@keyframes gradientShift {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* ---------- Generic fade-in ---------- */
@keyframes fadeInUp {
    from {opacity: 0; transform: translateY(14px);}
    to {opacity: 1; transform: translateY(0);}
}
.fade-in { animation: fadeInUp 0.55s ease forwards; }

/* ---------- Section headers ---------- */
.section-header {
    font-size: 21px;
    font-weight: 700;
    color: #e6edf3;
    border-left: 4px solid #20c997;
    padding-left: 12px;
    margin: 6px 0 16px 0;
    animation: fadeInUp 0.5s ease forwards;
}

/* ---------- KPI CARDS ---------- */
.kpi-card {
    background: linear-gradient(155deg, #1a2128 0%, #161c22 100%);
    padding: 20px 16px;
    border-radius: 18px;
    border: 1px solid #263039;
    text-align: center;
    box-shadow: 0 4px 18px rgba(0,0,0,0.30);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    animation: fadeInUp 0.55s ease forwards;
    position: relative;
    overflow: hidden;
}
.kpi-card:hover {
    transform: translateY(-6px) scale(1.015);
    box-shadow: 0 12px 28px rgba(32,201,151,0.22);
    border-color: #20c997;
}
.kpi-icon { font-size: 24px; margin-bottom: 4px; }
.kpi-title {
    color: #8a99a8;
    font-size: 12.5px;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-weight: 600;
}
.kpi-value {
    background: linear-gradient(90deg, #20c997, #0dcaf0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 28px;
    font-weight: 800;
    margin-top: 6px;
    line-height: 1.2;
}
.kpi-sub { color: #51606d; font-size: 11.5px; margin-top: 3px; }

/* ---------- Chart card wrapper (bordered containers) ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
    animation: fadeInUp 0.6s ease forwards;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #20c997 !important;
    box-shadow: 0 8px 24px rgba(32,201,151,0.12);
}

/* ---------- Buttons ---------- */
div.stButton > button, div.stDownloadButton > button {
    background: linear-gradient(90deg, #20c997, #0dcaf0);
    color: #0b0f12;
    font-weight: 700;
    border-radius: 10px;
    border: none;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    transform: scale(1.035);
    box-shadow: 0 6px 16px rgba(32,201,151,0.25);
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    justify-content: center;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    font-weight: 600;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #20c997;
}

/* ---------- Empty-state hero ---------- */
.hero-box {
    text-align: center;
    padding: 60px 20px;
    border-radius: 22px;
    border: 1.5px dashed #2d3946;
    animation: fadeInUp 0.6s ease forwards;
}

/* ---------- Auth page ---------- */
.auth-hero {
    text-align: center;
    margin: 18px auto 8px auto;
    animation: fadeInUp 0.5s ease forwards;
}
.auth-logo-badge {
    width: 64px;
    height: 64px;
    margin: 0 auto 14px auto;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    background: linear-gradient(135deg, rgba(32,201,151,0.18), rgba(13,202,240,0.18));
    border: 1px solid rgba(32,201,151,0.35);
    box-shadow: 0 8px 24px rgba(32,201,151,0.18);
}
.auth-title {
    text-align: center;
    font-size: 26px;
    font-weight: 800;
    color: #e6edf3;
    margin-bottom: 4px;
}
.auth-sub {
    text-align: center;
    color: #7d8a98;
    font-size: 14px;
    margin-bottom: 4px;
}

/* Style the real st.container(border=True) used for the auth card */
div[data-testid="stVerticalBlockBorderWrapper"].auth-card-target {
    max-width: 480px;
    margin: 0 auto;
}

/* ---------- Badge ---------- */
.role-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.badge-admin { background: rgba(132,94,247,0.18); color: #b197fc; border: 1px solid rgba(132,94,247,0.4); }
.badge-user { background: rgba(32,201,151,0.18); color: #20c997; border: 1px solid rgba(32,201,151,0.4); }

/* ---------- File pill ---------- */
.file-pill {
    padding: 10px 14px;
    border-radius: 12px;
    background: #161c22;
    border: 1px solid #263039;
    margin-bottom: 6px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────
def format_value(val):
    try:
        sign = "-" if val < 0 else ""
        val = abs(val)
        if val >= 1e9:
            return f"{sign}{val/1e9:.2f}B"
        if val >= 1e6:
            return f"{sign}{val/1e6:.2f}M"
        if val >= 1e3:
            return f"{sign}{val/1e3:.2f}K"
        return f"{sign}{val:,.2f}"
    except Exception:
        return str(val)


def kpi_card(col, icon, title, value, sub="", delay=0.0):
    col.markdown(
        f"""
        <div class="kpi-card" style="animation-delay:{delay}s;">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(text):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def style_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1"),
        margin=dict(t=30, b=10, l=10, r=10),
        transition=dict(duration=500, easing="cubic-in-out"),
        hoverlabel=dict(bgcolor="#1a2128", font_size=13, font_family="Inter"),
    )
    return fig


def read_df_from_bytes(raw_bytes: bytes, file_type: str) -> pd.DataFrame:
    if file_type == "csv":
        return pd.read_csv(io.BytesIO(raw_bytes))
    return pd.read_excel(io.BytesIO(raw_bytes))


CHART_COLORWAY = px.colors.qualitative.Prism
ACCENT = "#20c997"
ACCENT2 = "#2d3748"


# ──────────────────────────────────────────────────────────────────────────
# SESSION BOOTSTRAP — restore login from cookie if present
# ──────────────────────────────────────────────────────────────────────────
auth.try_restore_session()


# ──────────────────────────────────────────────────────────────────────────
# AUTH PAGE (login / signup) — shown when not logged in
# ──────────────────────────────────────────────────────────────────────────
def render_auth_page():
    st.write("")
    st.markdown(
        """
        <div class="auth-hero">
            <div class="auth-logo-badge">📊</div>
            <div class="auth-title">Smart Data Management System</div>
            <div class="auth-sub">আপলোড করুন, এক্সপ্লোর করুন, এডিট করুন এবং ভিজুয়ালাইজ করুন</div>
            <div class="auth-sub" style="font-size:12.5px; color:#51606d;">দ্রুত · পরিষ্কার · সম্পূর্ণ ইন্টারেক্টিভ</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        with st.container(border=True):
            tab_login, tab_signup = st.tabs(["🔑  লগইন", "📝  নতুন একাউন্ট"])

            with tab_login:
                st.markdown(
                    '<p style="text-align:center; color:#7d8a98; font-size:13.5px; margin:10px 0 18px 0;">'
                    'আপনার ড্যাশবোর্ডে প্রবেশ করতে লগইন করুন</p>',
                    unsafe_allow_html=True,
                )
                with st.form("login_form", clear_on_submit=False):
                    username = st.text_input("Username", placeholder="আপনার username লিখুন")
                    password = st.text_input("Password", type="password", placeholder="আপনার password লিখুন")
                    remember = st.checkbox("আমাকে লগইন রাখো (পরের বার আবার লগইন করতে হবে না)", value=True)
                    submitted = st.form_submit_button("লগইন করুন →", use_container_width=True)

                if submitted:
                    if not username or not password:
                        st.warning("⚠️ Username এবং Password দিন।")
                    else:
                        ok, msg = auth.login(username, password, remember=remember)
                        if ok:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

            with tab_signup:
                st.markdown(
                    '<p style="text-align:center; color:#7d8a98; font-size:13.5px; margin:10px 0 18px 0;">'
                    'নতুন একাউন্ট খুলে ডাটা আপলোড শুরু করুন</p>',
                    unsafe_allow_html=True,
                )
                with st.form("signup_form", clear_on_submit=True):
                    su_fullname = st.text_input("পুরো নাম (Full Name)", placeholder="যেমনঃ রাকিব হাসান")
                    su_username = st.text_input("Username", placeholder="ইউনিক একটি username দিন")
                    su_email = st.text_input("Email (ঐচ্ছিক)", placeholder="you@example.com")
                    su_password = st.text_input("Password", type="password", placeholder="কমপক্ষে ৪ অক্ষর")
                    su_password2 = st.text_input("Password আবার লিখুন", type="password")
                    su_submitted = st.form_submit_button("একাউন্ট তৈরি করুন →", use_container_width=True)

                if su_submitted:
                    if su_password != su_password2:
                        st.error("❌ দুটি Password মিলছে না।")
                    else:
                        ok, msg = db.create_user(su_username, su_password, su_fullname, su_email)
                        if ok:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")

        st.markdown(
            '<p style="text-align:center; color:#3d4b58; font-size:12px; margin-top:18px;">'
            '© 2026 Smart Data Management System</p>',
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────
# TOP BAR (shown once logged in) — user info + logout
# ──────────────────────────────────────────────────────────────────────────
def render_top_bar():
    user = auth.current_user()
    is_admin = auth.is_admin()

    left, right = st.columns([4, 1.3])
    with left:
        st.markdown('<div class="main-title">📊 Smart Data Management System</div>', unsafe_allow_html=True)
        badge_cls = "badge-admin" if is_admin else "badge-user"
        badge_txt = "ADMIN" if is_admin else "USER"
        name = user.get("full_name") or user.get("username")
        st.markdown(
            f'<div class="main-subtitle">👋 স্বাগতম, <b>{name}</b> &nbsp;'
            f'<span class="role-badge {badge_cls}">{badge_txt}</span></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.write("")
        if st.button("🚪 লগআউট", use_container_width=True):
            auth.logout()
            st.rerun()


# ──────────────────────────────────────────────────────────────────────────
# ADMIN DASHBOARD
# ──────────────────────────────────────────────────────────────────────────
def render_admin_dashboard():
    stats = db.get_admin_stats()

    section_header("📌 Platform Overview")
    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "👥", "Total Users", f"{stats['total_users']:,}", delay=0.0)
    kpi_card(c2, "📁", "Total Files Uploaded", f"{stats['total_files']:,}", delay=0.05)
    kpi_card(c3, "🆕", "Signups Today", f"{stats['signups_today']:,}", delay=0.10)
    kpi_card(c4, "⬆️", "Uploads Today", f"{stats['uploads_today']:,}", delay=0.15)

    st.write("")

    tab_users, tab_files, tab_activity = st.tabs(["👥 সব ব্যবহারকারী", "📁 সব ফাইল", "📜 Activity Log"])

    with tab_users:
        section_header("ব্যবহারকারীদের তালিকা ও সাইনআপ হিস্টরি")
        users = db.get_all_users()
        if not users:
            st.info("এখনো কোনো ব্যবহারকারী সাইনআপ করেননি।")
        else:
            udf = pd.DataFrame(users)
            udf = udf.rename(columns={
                "id": "ID", "username": "Username", "full_name": "Full Name",
                "email": "Email", "role": "Role", "created_at": "Signed Up At",
                "last_login": "Last Login", "file_count": "Files Uploaded",
            })
            st.dataframe(udf, use_container_width=True, hide_index=True)

            st.download_button(
                "⬇️ Users তালিকা CSV ডাউনলোড করুন",
                data=udf.to_csv(index=False).encode("utf-8"),
                file_name="all_users.csv",
                mime="text/csv",
            )

    with tab_files:
        section_header("সব ব্যবহারকারীর আপলোড করা ফাইল")
        files = db.get_all_files_admin()
        if not files:
            st.info("এখনো কোনো ফাইল আপলোড হয়নি।")
        else:
            fdf = pd.DataFrame(files)
            fdf = fdf.rename(columns={
                "id": "File ID", "file_name": "File Name", "uploaded_at": "Uploaded At",
                "rows": "Rows", "cols": "Columns", "file_type": "Type", "username": "Uploaded By",
            })
            st.dataframe(fdf, use_container_width=True, hide_index=True)

    with tab_activity:
        section_header("সাম্প্রতিক কার্যক্রম (Login / Signup / Logout)")
        acts = db.get_recent_activity(100)
        if not acts:
            st.info("কোনো activity রেকর্ড নেই।")
        else:
            adf = pd.DataFrame(acts)[["username", "action", "detail", "created_at"]]
            adf = adf.rename(columns={
                "username": "Username", "action": "Action", "detail": "Detail", "created_at": "Time",
            })
            st.dataframe(adf, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────────────
# USER DASHBOARD — upload, history, KPI, visualizations
# ──────────────────────────────────────────────────────────────────────────
def render_user_dashboard():
    user = auth.current_user()
    user_id = user["id"]

    with st.sidebar:
        st.markdown("### 📁 নতুন ডাটা আপলোড করুন")
        uploaded_file = st.file_uploader("CSV বা Excel ফাইল আপলোড করুন", type=["csv", "xlsx"])

        if uploaded_file is not None:
            if st.button("💾 সংরক্ষণ করুন (Save to history)", use_container_width=True):
                raw_bytes = uploaded_file.getvalue()
                file_type = "csv" if uploaded_file.name.endswith(".csv") else "xlsx"
                try:
                    temp_df = read_df_from_bytes(raw_bytes, file_type)
                    new_id = db.save_file(
                        user_id, uploaded_file.name, raw_bytes, file_type,
                        rows=temp_df.shape[0], cols=temp_df.shape[1],
                    )
                    db.log_activity(user_id, user["username"], "upload", f"ফাইল আপলোড: {uploaded_file.name}")
                    st.session_state.active_file_id = new_id
                    st.success(f"✅ '{uploaded_file.name}' সংরক্ষিত হয়েছে!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ ফাইল প্রসেস করতে সমস্যা হয়েছে: {e}")

        st.markdown("---")
        st.markdown("### 🗂️ আগের আপলোড করা ফাইল")
        history = db.get_user_files(user_id)

        if history:
            options = {f"{f['file_name']}  ·  {f['uploaded_at'][:16].replace('T', ' ')}": f["id"] for f in history}
            selected_label = st.selectbox("পুরনো ফাইল থেকে দেখুন:", list(options.keys()))
            selected_file_id = options[selected_label]

            colA, colB = st.columns(2)
            with colA:
                if st.button("📂 লোড করুন", use_container_width=True):
                    st.session_state.active_file_id = selected_file_id
                    st.rerun()
            with colB:
                if st.button("🗑️ ডিলিট", use_container_width=True):
                    db.delete_file(selected_file_id, user_id)
                    st.session_state.pop("active_file_id", None)
                    st.success("ফাইল ডিলিট হয়েছে।")
                    st.rerun()
        else:
            st.caption("এখনো কোনো ফাইল আপলোড করা হয়নি।")

        st.markdown("---")
        st.markdown(
            """
            **Tips**
            - Data tab-এ সরাসরি যেকোনো cell এডিট করুন
            - প্রতিটা চার্টের আলাদা X / Y selector আছে
            - আপলোড করা প্রতিটা ফাইল স্বয়ংক্রিয়ভাবে সংরক্ষিত হয় — পরে আবার লগইন করেও দেখতে পারবেন
            """
        )

    # ---- Determine which file is "active" right now ----
    active_file_id = st.session_state.get("active_file_id")
    if active_file_id is None and history:
        active_file_id = history[0]["id"]  # most recent by default
        st.session_state.active_file_id = active_file_id

    if active_file_id is None:
        st.markdown(
            """
            <div class="hero-box">
                <div style="font-size:50px;">📂</div>
                <div style="font-size:22px; font-weight:700; color:#e6edf3; margin-top:10px;">
                    শুরু করতে বাম পাশের sidebar থেকে একটি CSV বা Excel ফাইল আপলোড করুন
                </div>
                <div style="color:#7d8a98; margin-top:6px;">
                    এডিটেবল ডাটা টেবিল, স্মার্ট KPI কার্ড, এবং ৬টি সম্পূর্ণ কাস্টমাইজেবল চার্ট পাবেন —
                    প্রতিটির নিজস্ব X / Y axis selector সহ। আপলোড করা ফাইল স্বয়ংক্রিয়ভাবে সংরক্ষিত থাকবে।
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    df, fname = db.get_file_dataframe(active_file_id, user_id)
    if df is None:
        st.warning("নির্বাচিত ফাইলটি খুঁজে পাওয়া যায়নি। অন্য একটি ফাইল নির্বাচন করুন।")
        return

    st.caption(f"📄 বর্তমানে দেখানো হচ্ছে: **{fname}**")

    try:
        rows, cols = df.shape
        missing = int(df.isna().sum().sum())
        duplicates = int(df.duplicated().sum())

        i1, i2, i3, i4 = st.columns(4)
        kpi_card(i1, "📋", "Total Rows", f"{rows:,}", delay=0.0)
        kpi_card(i2, "🧩", "Total Columns", f"{cols:,}", delay=0.05)
        kpi_card(i3, "⚠️", "Missing Values", f"{missing:,}", delay=0.10)
        kpi_card(i4, "♻️", "Duplicate Rows", f"{duplicates:,}", delay=0.15)

        st.write("")

        tab_data, tab_kpi, tab_viz = st.tabs(["🗂️ Data Editor", "📌 KPI Overview", "📊 Visualizations"])

        # ════════════════════════════════════════════════════════════
        # TAB 1 — DATA EDITOR
        # ════════════════════════════════════════════════════════════
        with tab_data:
            section_header("Data View & Editing")

            search_query = st.text_input("🔍 Search data:")

            if search_query:
                mask = df.astype(str).apply(
                    lambda x: x.str.contains(search_query, case=False, na=False)
                ).any(axis=1)
                filtered_df = df[mask]
            else:
                filtered_df = df

            edited_df = st.data_editor(
                filtered_df, use_container_width=True, num_rows="dynamic", key=f"editor_{active_file_id}"
            )

            d1, d2, d3 = st.columns([1, 1, 4])
            with d1:
                st.download_button(
                    "⬇️ CSV ডাউনলোড",
                    data=edited_df.to_csv(index=False).encode("utf-8"),
                    file_name="edited_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with d2:
                if st.button("🔄 পরিবর্তন সেভ করুন", use_container_width=True):
                    new_bytes = edited_df.to_csv(index=False).encode("utf-8")
                    db.save_file(
                        user_id, fname.rsplit(".", 1)[0] + "_edited.csv", new_bytes, "csv",
                        rows=edited_df.shape[0], cols=edited_df.shape[1],
                    )
                    st.success("✅ এডিট করা ভার্সন নতুন এন্ট্রি হিসেবে history-তে সেভ হয়েছে।")
                    st.rerun()
            with d3:
                st.caption(f"Showing **{len(edited_df):,}** of **{len(df):,}** rows")

        numeric_cols = edited_df.select_dtypes(include=["number"]).columns.tolist()
        all_cols = edited_df.columns.tolist()

        # ════════════════════════════════════════════════════════════
        # TAB 2 — KPI OVERVIEW
        # ════════════════════════════════════════════════════════════
        with tab_kpi:
            section_header("Statistics (KPI Overview)")

            if numeric_cols:
                selected_stat_col = st.selectbox("Select column for statistics:", numeric_cols, key="kpi_col")

                col_data = edited_df[selected_stat_col].dropna()
                total_sum = col_data.sum()
                avg_val = col_data.mean()
                median_val = col_data.median()
                min_val = col_data.min()
                max_val = col_data.max()

                k1, k2, k3, k4, k5 = st.columns(5)
                kpi_card(k1, "Σ", f"Total {selected_stat_col}", format_value(total_sum), delay=0.0)
                kpi_card(k2, "📈", "Average", format_value(avg_val), delay=0.05)
                kpi_card(k3, "🎯", "Median", format_value(median_val), delay=0.10)
                kpi_card(k4, "🔻", "Minimum", format_value(min_val), delay=0.15)
                kpi_card(k5, "🔺", "Maximum", format_value(max_val), delay=0.20)
            else:
                st.info("No numeric columns found in this dataset to compute statistics.")

        # ════════════════════════════════════════════════════════════
        # TAB 3 — VISUALIZATIONS
        # ════════════════════════════════════════════════════════════
        with tab_viz:
            section_header("Data Visualization")

            if not numeric_cols:
                st.info("No numeric columns found — add some numeric data to unlock charts.")
            else:
                NONE_OPT = "— None —"

                r1c1, r1c2 = st.columns(2)

                with r1c1:
                    with st.container(border=True):
                        st.markdown("#### 📊 Bar Chart")
                        bx1, bx2, bx3 = st.columns(3)
                        bar_x = bx1.selectbox("X-Axis", all_cols, key="bar_x")
                        bar_y = bx2.selectbox("Y-Axis", numeric_cols, key="bar_y")
                        bar_agg = bx3.selectbox("Aggregation", ["sum", "mean", "count", "max", "min"], key="bar_agg")

                        data = edited_df.groupby(bar_x, as_index=False)[bar_y].agg(bar_agg)
                        peak = data[bar_y].max()
                        colors = [ACCENT if v == peak else ACCENT2 for v in data[bar_y]]

                        fig_bar = go.Figure(
                            data=[
                                go.Bar(
                                    x=data[bar_x],
                                    y=data[bar_y],
                                    marker_color=colors,
                                    text=[format_value(v) for v in data[bar_y]],
                                    textposition="outside",
                                    hovertemplate="<b>%{x}</b><br>Value: %{y:,.2f}<extra></extra>",
                                )
                            ]
                        )
                        fig_bar.update_traces(marker=dict(cornerradius=10), cliponaxis=False)
                        fig_bar.update_layout(
                            bargap=0.55,
                            showlegend=False,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=False, showticklabels=False),
                        )
                        st.plotly_chart(style_fig(fig_bar), use_container_width=True)

                with r1c2:
                    with st.container(border=True):
                        st.markdown("#### 🍩 Donut Chart")
                        px1, px2 = st.columns(2)
                        pie_l = px1.selectbox("Category", all_cols, key="pie_label")
                        pie_v = px2.selectbox("Value", numeric_cols, key="pie_v")

                        data_p = edited_df.groupby(pie_l, as_index=False)[pie_v].sum()
                        fig_pie = px.pie(
                            data_p, values=pie_v, names=pie_l, hole=0.55,
                            color_discrete_sequence=CHART_COLORWAY,
                        )
                        fig_pie.update_traces(
                            hovertemplate="<b>%{label}</b><br>Value: %{value:,.2f}<extra></extra>",
                            textfont=dict(size=12),
                        )
                        st.plotly_chart(style_fig(fig_pie), use_container_width=True)

                r2c1, r2c2 = st.columns(2)

                with r2c1:
                    with st.container(border=True):
                        st.markdown("#### 📈 Line Chart")
                        lx1, lx2, lx3 = st.columns(3)
                        line_x = lx1.selectbox("X-Axis", all_cols, key="line_x")
                        line_y = lx2.selectbox("Y-Axis", numeric_cols, key="line_y")
                        line_group = lx3.selectbox("Group / Color (optional)", [NONE_OPT] + all_cols, key="line_group")

                        sorted_df = edited_df.sort_values(by=line_x)
                        if line_group != NONE_OPT:
                            fig_line = px.line(
                                sorted_df, x=line_x, y=line_y, color=line_group,
                                markers=True, color_discrete_sequence=CHART_COLORWAY,
                            )
                        else:
                            fig_line = px.line(
                                sorted_df, x=line_x, y=line_y,
                                markers=True, color_discrete_sequence=[ACCENT],
                            )
                        fig_line.update_traces(line=dict(width=3))
                        fig_line.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#222b33"))
                        st.plotly_chart(style_fig(fig_line), use_container_width=True)

                with r2c2:
                    with st.container(border=True):
                        st.markdown("#### 🌄 Area Chart")
                        ax1, ax2 = st.columns(2)
                        area_x = ax1.selectbox("X-Axis", all_cols, key="area_x")
                        area_y = ax2.selectbox("Y-Axis", numeric_cols, key="area_y")

                        sorted_area = edited_df.sort_values(by=area_x)
                        fig_area = px.area(
                            sorted_area, x=area_x, y=area_y,
                            color_discrete_sequence=[ACCENT],
                        )
                        fig_area.update_traces(line=dict(width=2.5), fillcolor="rgba(32,201,151,0.25)")
                        fig_area.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#222b33"))
                        st.plotly_chart(style_fig(fig_area), use_container_width=True)

                r3c1, r3c2 = st.columns(2)

                with r3c1:
                    with st.container(border=True):
                        st.markdown("#### ✨ Scatter Plot")
                        sx1, sx2, sx3, sx4 = st.columns(4)
                        scat_x = sx1.selectbox("X-Axis", numeric_cols, key="scat_x")
                        scat_y = sx2.selectbox("Y-Axis", numeric_cols, key="scat_y")
                        scat_color = sx3.selectbox("Color (optional)", [NONE_OPT] + all_cols, key="scat_color")
                        scat_size = sx4.selectbox("Size (optional)", [NONE_OPT] + numeric_cols, key="scat_size")

                        fig_scatter = px.scatter(
                            edited_df,
                            x=scat_x,
                            y=scat_y,
                            color=None if scat_color == NONE_OPT else scat_color,
                            size=None if scat_size == NONE_OPT else scat_size,
                            color_discrete_sequence=CHART_COLORWAY,
                        )
                        fig_scatter.update_traces(marker=dict(opacity=0.85, line=dict(width=0.5, color="#0b0f12")))
                        fig_scatter.update_layout(
                            xaxis=dict(showgrid=True, gridcolor="#222b33"),
                            yaxis=dict(showgrid=True, gridcolor="#222b33"),
                        )
                        st.plotly_chart(style_fig(fig_scatter), use_container_width=True)

                with r3c2:
                    with st.container(border=True):
                        st.markdown("#### 📦 Histogram")
                        hx1, hx2 = st.columns(2)
                        hist_col = hx1.selectbox("Column", numeric_cols, key="hist_col")
                        hist_bins = hx2.slider("Bins", min_value=5, max_value=100, value=30, key="hist_bins")

                        fig_hist = px.histogram(
                            edited_df, x=hist_col, nbins=hist_bins,
                            color_discrete_sequence=[ACCENT],
                        )
                        fig_hist.update_traces(marker=dict(line=dict(width=0)))
                        fig_hist.update_layout(
                            bargap=0.05,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=True, gridcolor="#222b33"),
                        )
                        st.plotly_chart(style_fig(fig_hist), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")


# ──────────────────────────────────────────────────────────────────────────
# ROUTER
# ──────────────────────────────────────────────────────────────────────────
if not auth.is_logged_in():
    render_auth_page()
else:
    render_top_bar()
    st.write("")
    if auth.is_admin():
        render_admin_dashboard()
    else:
        render_user_dashboard()