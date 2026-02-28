import math
import time
from datetime import datetime

import streamlit as st

from app.components.enhanced_header import render_enhanced_issue_header
from app.i18n import LANG_OPTIONS, t
from app.managers.fs_issue_manager import FileModifiedExternallyError, FileSystemIssueManager

# --- Page Config ---
st.set_page_config(page_title=t("app_title"), page_icon="📁", layout="wide", initial_sidebar_state="expanded")

# --- Constants ---
PAGE_SIZE = 15


# --- Initialize Manager & State ---
@st.cache_resource
def get_manager():
    return FileSystemIssueManager()


manager = get_manager()

# Core State
if "current_view" not in st.session_state:
    st.session_state.current_view = "index"  # 'index', 'all_issues', 'create', 'settings', 'issue_detail'
if "selected_issue_id" not in st.session_state:
    st.session_state.selected_issue_id = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# Filter State
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "filter_status" not in st.session_state:
    st.session_state.filter_status = "All"  # "All" or native status
if "filter_tag" not in st.session_state:
    st.session_state.filter_tag = "All"
if "filter_assignee" not in st.session_state:
    st.session_state.filter_assignee = "All"
if "filter_project" not in st.session_state:
    st.session_state.filter_project = "All"
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "Time (Newest)"

# Pagination State
if "current_page" not in st.session_state:
    st.session_state.current_page = 1

# Batch Mode State
if "batch_mode" not in st.session_state:
    st.session_state.batch_mode = False
if "batch_selected" not in st.session_state:
    st.session_state.batch_selected = set()

if "_lang" not in st.session_state:
    # Let i18n get_lang handle this, but initialize default
    st.session_state._lang = "en"


def nav_to(view_name, issue_id=None):
    st.session_state.current_view = view_name
    st.session_state.selected_issue_id = issue_id
    st.session_state.edit_mode = False
    st.session_state.batch_mode = False
    st.session_state.batch_selected = set()
    st.rerun()


# --- Helper Functions ---
def format_timestamp(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def get_status_color(status):
    colors = {"OPEN": "red", "IN-PROGRESS": "orange", "FIXED": "green", "CLOSED": "gray"}
    return colors.get(status, "blue")


# --- UI Components ---


def render_breadcrumb(path_tuples):
    """
    Renders clickable breadcrumbs: [(label, target_view, target_id), ...]
    Using st.columns.
    """
    total = len(path_tuples)
    if total == 0:
        return

    weights = []
    for i, _ in enumerate(path_tuples):
        weights.append(3)
        if i < total - 1:
            weights.append(1)
    weights.append(15)  # Pad end

    cols = st.columns(weights)
    for i, (label, view, target_id) in enumerate(path_tuples):
        col_idx = i * 2
        with cols[col_idx]:
            if i == total - 1:
                st.markdown(
                    f"<span style='color: gray; font-size: 0.9em; line-height: 2.5;'>{label}</span>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(label, key=f"bc_{i}_{view}_{target_id}", type="tertiary", use_container_width=True):
                    nav_to(view, target_id)

        if i < total - 1:
            with cols[col_idx + 1]:
                st.markdown(
                    "<div style='text-align: center; color: gray; font-size: 1.2rem; line-height: 1.8;'>›</div>",
                    unsafe_allow_html=True,
                )


def render_sidebar():
    st.sidebar.title(t("sidebar_title"))

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button(t("nav_new_issue"), use_container_width=True, type="primary"):
        nav_to("create")

    st.sidebar.markdown("### " + t("nav_main_views"))

    if st.sidebar.button(
        "🏠 " + t("nav_dashboard"),
        use_container_width=True,
        type="primary" if st.session_state.current_view == "index" else "secondary",
    ):
        nav_to("index")

    if st.sidebar.button(
        "📋 " + t("nav_all_issues"),
        use_container_width=True,
        type="primary" if st.session_state.current_view == "all_issues" else "secondary",
    ):
        st.session_state.filter_status = "All"
        st.session_state.current_page = 1
        nav_to("all_issues")

    st.sidebar.markdown("### " + t("nav_quick_filters"))
    # Quick filter buttons
    for status in manager.VALID_STATUSES:
        icon = {"OPEN": "🔴", "IN-PROGRESS": "🟠", "FIXED": "🟢", "CLOSED": "⚪"}.get(status.upper(), "👉")
        # translated status
        label = f"{icon} {t('status_' + status.lower(), None) if t('status_' + status.lower()) != 'status_' + status.lower() else status.upper()}"
        is_active = st.session_state.current_view == "all_issues" and st.session_state.filter_status == status
        if st.sidebar.button(label, use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.filter_status = status
            st.session_state.current_page = 1
            nav_to("all_issues")

    st.sidebar.markdown("### " + t("nav_system"))
    if st.sidebar.button(
        "⚙️ " + t("nav_settings"),
        use_container_width=True,
        type="primary" if st.session_state.current_view == "settings" else "secondary",
    ):
        nav_to("settings")

    # Spacer
    for _ in range(5):
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # Language Selector at bottom
    lang_choice = st.sidebar.selectbox(
        t("lang_selector_label"),
        list(LANG_OPTIONS.keys()),
        index=list(LANG_OPTIONS.values()).index(st.session_state._lang),
        key="lang_selectbox",
    )
    new_lang = LANG_OPTIONS[lang_choice]
    if new_lang != st.session_state._lang:
        st.session_state._lang = new_lang
        st.query_params["lang"] = new_lang
        st.rerun()


def _render_all_issues_toolbar():
    """Renders the horizontal filter/sort toolbar and returns the current filter values."""
    with st.container(border=True):
        col_s, col_st, col_as, col_pr, col_tg, col_sort = st.columns(6)
        with col_s:
            search_query = st.text_input(
                "🔍 " + t("filter_keyword_label"),
                value=st.session_state.search_query,
                label_visibility="collapsed",
                placeholder=t("filter_keyword_placeholder"),
            ).lower()
        with col_st:
            filter_status = st.selectbox(
                t("filter_status"),
                ["All"] + manager.VALID_STATUSES,
                index=(
                    0
                    if st.session_state.filter_status == "All"
                    else manager.VALID_STATUSES.index(st.session_state.filter_status) + 1
                ),
                label_visibility="collapsed",
            )
        with col_as:
            all_users = manager.get_users()
            filter_assignee = st.selectbox(
                t("filter_assignee"),
                ["All"] + all_users,
                index=(
                    0
                    if st.session_state.filter_assignee == "All"
                    else all_users.index(st.session_state.filter_assignee) + 1
                ),
                label_visibility="collapsed",
            )
        with col_pr:
            all_projects = manager.get_projects()
            filter_project = st.selectbox(
                t("filter_project"),
                ["All"] + all_projects,
                index=(
                    0
                    if st.session_state.filter_project == "All"
                    else all_projects.index(st.session_state.filter_project) + 1
                ),
                label_visibility="collapsed",
            )
        with col_tg:
            all_tags = manager.get_tags()
            filter_tag = st.selectbox(
                t("filter_tags"),
                ["All"] + all_tags,
                index=0 if st.session_state.filter_tag == "All" else all_tags.index(st.session_state.filter_tag) + 1,
                label_visibility="collapsed",
            )
        with col_sort:
            sort_by = st.selectbox(
                t("sort_by"), ["Time (Newest)", "Time (Oldest)", "Time (Updated)"], label_visibility="collapsed"
            )

    # Detect filter change to reset pagination
    filter_changed = (
        search_query != st.session_state.search_query
        or filter_status != st.session_state.filter_status
        or filter_assignee != st.session_state.filter_assignee
        or filter_project != st.session_state.filter_project
        or filter_tag != st.session_state.filter_tag
        or sort_by != st.session_state.sort_by
    )

    if filter_changed:
        st.session_state.search_query = search_query
        st.session_state.filter_status = filter_status
        st.session_state.filter_assignee = filter_assignee
        st.session_state.filter_project = filter_project
        st.session_state.filter_tag = filter_tag
        st.session_state.sort_by = sort_by
        st.session_state.current_page = 1

    return {
        "search_query": search_query,
        "filter_status": filter_status,
        "filter_assignee": filter_assignee,
        "filter_project": filter_project,
        "filter_tag": filter_tag,
        "sort_by": sort_by,
        "all_users": all_users,
    }


def _apply_issue_filters_and_sort(issues, filters):
    """Filters and sorts the issues list based on provided filters."""
    filtered = []
    for issue in issues:
        if filters["filter_status"] != "All" and issue.get("status", "").lower() != filters["filter_status"].lower():
            continue
        if filters["filter_assignee"] != "All" and issue.get("assignee") != filters["filter_assignee"]:
            continue
        if filters["filter_project"] != "All" and issue.get("project") != filters["filter_project"]:
            continue
        if filters["filter_tag"] != "All" and filters["filter_tag"] not in issue.get("tags", []):
            continue
        if (
            filters["search_query"]
            and filters["search_query"] not in issue["title"].lower()
            and filters["search_query"] not in issue["id"].lower()
        ):
            continue
        filtered.append(issue)

    # Sort
    sort_by = filters["sort_by"]
    if sort_by == "Time (Newest)":
        filtered.sort(key=lambda x: x["created_at"], reverse=True)
    elif sort_by == "Time (Oldest)":
        filtered.sort(key=lambda x: x["created_at"], reverse=False)
    else:
        filtered.sort(key=lambda x: x["last_modified"], reverse=True)

    return filtered


def _render_batch_actions(all_users):
    """Renders the batch actions toggle and logic."""
    col_batch, col_batch_actions = st.columns([1, 4])
    with col_batch:
        st.session_state.batch_mode = st.toggle(t("batch_mode"), value=st.session_state.batch_mode)

    if st.session_state.batch_mode:
        with col_batch_actions:
            sel_count = len(st.session_state.batch_selected)
            if sel_count > 0:
                bc1, bc2, bc3 = st.columns(3)
                with bc1:
                    new_status = st.selectbox(
                        t("batch_status_label"), ["--"] + manager.VALID_STATUSES, label_visibility="collapsed"
                    )
                with bc2:
                    new_assignee = st.selectbox(t("meta_assignee"), ["--"] + all_users, label_visibility="collapsed")
                with bc3:
                    if st.button(t("batch_btn_apply").format(sel_count), type="primary"):
                        updates = {}
                        if new_assignee != "--":
                            updates["assignee"] = new_assignee
                        if updates:
                            manager.batch_update_metadata(list(st.session_state.batch_selected), updates)
                        if new_status != "--":
                            manager.batch_change_status(list(st.session_state.batch_selected), new_status)
                        st.session_state.batch_selected = set()
                        st.success(t("batch_success"))
                        time.sleep(0.5)
                        st.rerun()


def _render_pagination_controls(total_issues, total_pages):
    """Renders the pagination footer."""
    p1, p2, p3 = st.columns([1, 2, 1])
    with p1:
        if st.session_state.current_page > 1:
            if st.button("⬅ " + t("page_prev"), use_container_width=True, type="tertiary"):
                st.session_state.current_page -= 1
                st.rerun()
    with p2:
        st.markdown(
            f"<div style='text-align: center; padding-top: 5px;'>{t('page_indicator').format(st.session_state.current_page, total_pages)} ({total_issues}总计)</div>",
            unsafe_allow_html=True,
        )
    with p3:
        if st.session_state.current_page < total_pages:
            if st.button(t("page_next") + " ➡", use_container_width=True, type="tertiary"):
                st.session_state.current_page += 1
                st.rerun()


def render_all_issues(issues):
    render_breadcrumb([(t("nav_dashboard"), "index", None), (t("nav_all_issues"), "all_issues", None)])
    st.header(t("nav_all_issues"))

    filters = _render_all_issues_toolbar()
    filtered = _apply_issue_filters_and_sort(issues, filters)

    _render_batch_actions(filters["all_users"])

    st.divider()

    # Pagination Logic
    total_issues = len(filtered)
    total_pages = max(1, math.ceil(total_issues / PAGE_SIZE))
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = total_pages

    start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_issues = filtered[start_idx:end_idx]

    # Data List Rendering
    if not page_issues:
        st.info("👻 " + t("index_no_issues"))
    else:
        for issue in page_issues:
            with st.container(border=True):
                c0, c1, c2, c3, c4 = st.columns([0.5, 4, 1.5, 1.5, 1])
                with c0:
                    if st.session_state.batch_mode:
                        is_sel = issue["id"] in st.session_state.batch_selected
                        if st.checkbox(" ", key=f"chk_{issue['id']}", value=is_sel, label_visibility="collapsed"):
                            st.session_state.batch_selected.add(issue["id"])
                        else:
                            st.session_state.batch_selected.discard(issue["id"])
                    else:
                        st.markdown(f"**[{issue['type']}]**")
                with c1:
                    st.markdown(f"**{issue['title']}**")
                    tags_html = " ".join([f"`{t}`" for t in issue.get("tags", [])])
                    st.caption(f"🔖 {issue['id']} {tags_html}")
                with c2:
                    color = get_status_color(issue["status"].upper())
                    st.markdown(f":{color}[**{issue['status'].upper()}**]")
                with c3:
                    assignee = issue.get("assignee") or "—"
                    st.markdown(f"👤 {assignee}")
                    st.caption(f"🕒 {format_timestamp(issue['last_modified'])}")
                with c4:
                    if st.button("➔", key=f"navbtn_{issue['id']}", use_container_width=True, type="tertiary"):
                        nav_to("issue_detail", issue["id"])

    _render_pagination_controls(total_issues, total_pages)


def render_create_view():
    render_breadcrumb([(t("nav_dashboard"), "index", None), (t("create_header"), "create", None)])
    st.header(t("create_header"))

    col1, col2 = st.columns([1, 1])
    with col1:
        issue_type = st.selectbox(t("create_type"), ["bug", "fea", "opt", "doc", "task"])
    with col2:
        title = st.text_input(t("create_title"), max_chars=50)

    content = st.text_area(t("create_content"), height=400)

    with st.expander(t("create_extra")):
        users = [""] + manager.get_users()
        projects = [""] + manager.get_projects()
        available_tags = manager.get_tags()

        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            assignee = st.selectbox(t("meta_assignee"), users)
        with col_meta2:
            project = st.selectbox(t("meta_project"), projects)

        priority = st.selectbox(t("meta_priority"), ["Low", "Medium", "High", "Critical"])
        selected_tags = st.multiselect(t("meta_tags"), available_tags)

    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        if st.button(t("create_btn_submit"), type="primary"):
            if title:
                extra = {}
                if assignee:
                    extra["assignee"] = assignee
                if project:
                    extra["project"] = project
                if priority:
                    extra["priority"] = priority
                if selected_tags:
                    extra["tags"] = selected_tags

                new_id = manager.create_issue(issue_type, title, content, extra)
                st.success(t("create_success").format(new_id))
                time.sleep(0.5)
                nav_to("issue_detail", new_id)
            else:
                st.error(t("create_error_title"))

    with col2:
        if st.button(t("create_btn_cancel")):
            nav_to("index")


@st.dialog(t("conflict_title"))
def show_conflict_dialog(error_msg):
    st.error(error_msg)
    st.write(t("conflict_info"))
    if st.button(t("conflict_btn_reload")):
        st.session_state.edit_mode = False
        st.rerun()


def _render_issue_header(issue):
    """Renders breadcrumbs and the issue title/basic info."""
    render_breadcrumb(
        [
            (t("nav_dashboard"), "index", None),
            (t("nav_all_issues"), "all_issues", None),
            (f"[{issue['type']}] {issue['title']}", "issue_detail", issue["id"]),
        ]
    )

    st.markdown(f"## 📄 `[{issue['type']}]` {issue['title']}")

    current_tags = issue.get("tags", [])
    if current_tags:
        tags_html = " | ".join([f"🏷️ `{tag}`" for tag in current_tags])
        st.caption(
            f"{t('issue_path_label').format(issue['filepath'], format_timestamp(issue['last_modified']))} | {tags_html}"
        )
    else:
        st.caption(t("issue_path_label").format(issue["filepath"], format_timestamp(issue["last_modified"])))


def _render_status_transitions(issue_id, issue_status):
    """Renders the row of status transition buttons with arrows."""
    statuses = manager.VALID_STATUSES
    weights = []
    for _ in range(len(statuses)):
        weights.append(4)
        weights.append(1)
    weights.pop()
    cols = st.columns(weights)

    for i, status in enumerate(statuses):
        col_idx = i * 2
        with cols[col_idx]:
            trans_label = t(f"status_{status}") if t(f"status_{status}") != f"status_{status}" else status.upper()
            if status.lower() == issue_status.lower():
                st.button(
                    f"✓ {trans_label}", key=f"mv_{status}_cur", use_container_width=True, type="primary", disabled=True
                )
            else:
                if st.button(trans_label, key=f"mv_{status}", use_container_width=True, type="secondary"):
                    if manager.change_status(issue_id, status.lower()):
                        st.toast(t("issue_moved").format(trans_label))
                        time.sleep(0.5)
                        st.rerun()
        if i < len(statuses) - 1:
            with cols[col_idx + 1]:
                st.markdown(
                    "<div style='text-align: center; color: #adb5bd; font-size: 1.5rem; line-height: 2.2;'>➔</div>",
                    unsafe_allow_html=True,
                )


def _render_issue_content(issue):
    """Renders the markdown content or the editor."""
    if st.session_state.edit_mode:
        new_content = st.text_area(t("issue_edit_content_label"), value=issue["content"], height=500)
        frontend_mtime = issue["last_modified"]

        if st.button(t("issue_btn_save"), type="primary"):
            try:
                manager.save_issue_content(issue["id"], new_content, frontend_mtime)
                st.success(t("issue_save_success"))
                st.session_state.edit_mode = False
                time.sleep(0.5)
                st.rerun()
            except FileModifiedExternallyError as e:
                show_conflict_dialog(str(e))
    else:
        st.markdown(issue["content"])
        st.divider()


def _render_issue_attachments_and_comments(issue):
    """Renders the uploader and comment form in an expander."""
    with st.expander("📎 / 💬 Attachment & Comment"):
        uploaded_file = st.file_uploader(t("issue_upload_label"), key="file_uploader")
        if uploaded_file is not None:
            attachments_dir = manager.base_dir / "attachments"
            attachments_dir.mkdir(exist_ok=True)
            safe_name = f"{int(time.time())}_{uploaded_file.name}"
            file_path = attachments_dir / safe_name
            file_path.write_bytes(uploaded_file.getbuffer())

            if uploaded_file.type.startswith("image/"):
                attachment_md = f"\n\n{t('attach_img_md').format(uploaded_file.name, safe_name)}"
            else:
                attachment_md = f"\n\n{t('attach_link_md').format(uploaded_file.name, safe_name)}"

            try:
                manager.save_issue_content(issue["id"], issue["content"] + attachment_md, issue["last_modified"])
                st.success(t("issue_upload_success"))
                time.sleep(1)
                st.rerun()
            except FileModifiedExternallyError as e:
                show_conflict_dialog(str(e))

        new_comment = st.text_area(t("issue_comment_label"), placeholder=t("issue_comment_placeholder"), height=100)
        if st.button(t("issue_btn_comment"), type="primary"):
            if new_comment.strip():
                comment_text = f"\n\n{t('comment_header_md').format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), new_comment.strip())}"
                try:
                    manager.save_issue_content(issue["id"], issue["content"] + comment_text, issue["last_modified"])
                    st.success(t("issue_comment_success"))
                    time.sleep(0.5)
                    st.rerun()
                except FileModifiedExternallyError as e:
                    show_conflict_dialog(str(e))


def _render_metadata_sidebar(issue):
    """Renders the properties panel on the right side."""
    with st.container(border=True):
        st.markdown(t("meta_title"))

        users = [""] + manager.get_users()
        current_assignee = issue.get("assignee", "")
        if current_assignee and current_assignee not in users:
            users.append(current_assignee)

        projects = [""] + manager.get_projects()
        current_project = issue.get("project", "")
        if current_project and current_project not in projects:
            projects.append(current_project)

        available_tags = manager.get_tags()
        current_tags = issue.get("tags", [])
        for tag in current_tags:
            if tag not in available_tags:
                available_tags.append(tag)

        assignee = st.selectbox(
            t("meta_assignee"), users, index=users.index(current_assignee) if current_assignee in users else 0
        )
        project = st.selectbox(
            t("meta_project"), projects, index=projects.index(current_project) if current_project in projects else 0
        )
        priority = st.selectbox(
            t("meta_priority"),
            ["Low", "Medium", "High", "Critical"],
            index=(
                ["Low", "Medium", "High", "Critical"].index(issue.get("priority", "Low"))
                if issue.get("priority", "Low") in ["Low", "Medium", "High", "Critical"]
                else 0
            ),
        )
        tags = st.multiselect(t("meta_tags"), available_tags, default=current_tags)

        if st.button(t("meta_btn_update"), key="update_meta", use_container_width=True):
            manager.update_metadata(
                issue["id"], {"assignee": assignee, "project": project, "priority": priority, "tags": tags}
            )
            st.toast(t("meta_update_success"))
            time.sleep(0.5)
            st.rerun()


def render_issue_view(issue_id):
    try:
        issue = manager.get_issue(issue_id)
    except Exception as e:
        st.error(t("issue_load_error").format(e))
        if st.button(t("issue_btn_back")):
            nav_to("all_issues")
        return

    # 使用增强的头部组件
    render_enhanced_issue_header(issue, manager)

    # 主体内容区
    col_main, col_meta = st.columns([3, 1])

    with col_main:
        _render_issue_content(issue)
        if not st.session_state.edit_mode:
            _render_issue_attachments_and_comments(issue)

    # 元数据侧边栏
    with col_meta:
        _render_metadata_sidebar(issue)


def render_dashboard(issues):
    st.header("🏠 " + t("dashboard_header"))
    st.divider()

    total = len(issues)
    open_count = len([i for i in issues if i["status"].lower() == "open"])
    inprog_count = len([i for i in issues if i["status"].lower() == "in-progress"])
    fixed_count = len([i for i in issues if i["status"].lower() == "fixed"])
    closed_count = len([i for i in issues if i["status"].lower() == "closed"])

    # High level metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container(border=True):
            st.metric("📦 " + t("dashboard_total"), total)
    with col2:
        with st.container(border=True):
            st.metric("🔴 " + t("dashboard_open"), open_count)
    with col3:
        with st.container(border=True):
            st.metric("🟠 " + t("dashboard_in_progress"), inprog_count)
    with col4:
        with st.container(border=True):
            st.metric("🟢⚪ " + t("dashboard_fixed") + "/" + t("dashboard_closed"), fixed_count + closed_count)

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🕑 " + t("dashboard_recent"))
        recent_issues = sorted(issues, key=lambda x: x["last_modified"], reverse=True)[:10]

        if not recent_issues:
            st.info(t("index_no_issues"))
        else:
            for issue in recent_issues:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"🎫 **[{issue['type']}]** {issue['title']}")
                        assignee_display = issue.get("assignee") or "—"
                        st.caption(
                            f"🕒 {format_timestamp(issue['last_modified'])} | 👤 {assignee_display} | 🚥 {issue['status']}"
                        )
                    with c2:
                        if st.button("➔", key=f"d_nav_{issue['id']}", use_container_width=True, type="tertiary"):
                            nav_to("issue_detail", issue["id"])

    with col_right:
        st.subheader("💡 " + t("index_quick_start"))
        st.info(t("index_quick_start_content"))

        st.divider()
        st.subheader(t("dashboard_by_type"))
        type_counts = {}
        for i in issues:
            tp = i.get("type", "unknown").upper()
            type_counts[tp] = type_counts.get(tp, 0) + 1
        if type_counts:
            st.bar_chart(type_counts)


def render_settings_view():
    render_breadcrumb([(t("nav_dashboard"), "index", None), (t("nav_settings"), "settings", None)])
    st.header(t("settings_header"))
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.subheader(t("settings_users_header"))
            new_user = st.text_input(t("settings_add_user"), key="new_user_input")
            if st.button(t("settings_btn_add_user"), use_container_width=True) and new_user:
                manager.add_user(new_user)
                st.success(t("settings_user_added").format(new_user))
                time.sleep(0.5)
                st.rerun()

            existing_users = manager.get_users()
            if existing_users:
                st.divider()
                user_to_delete = st.selectbox(t("settings_current_users"), [""] + existing_users)
                if user_to_delete and st.button(f"🗑 {user_to_delete}", use_container_width=True, type="tertiary"):
                    manager.remove_user(user_to_delete)
                    st.success("✅")
                    time.sleep(0.5)
                    st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader(t("settings_projects_header"))
            new_project = st.text_input(t("settings_add_project"), key="new_project_input")
            if st.button(t("settings_btn_add_project"), use_container_width=True) and new_project:
                manager.add_project(new_project)
                st.success(t("settings_project_added").format(new_project))
                time.sleep(0.5)
                st.rerun()

            existing_projects = manager.get_projects()
            if existing_projects:
                st.divider()
                project_to_delete = st.selectbox(t("settings_current_projects"), [""] + existing_projects)
                if project_to_delete and st.button(f"🗑 {project_to_delete}", use_container_width=True, type="tertiary"):
                    manager.remove_project(project_to_delete)
                    st.success("✅")
                    time.sleep(0.5)
                    st.rerun()

    with col3:
        with st.container(border=True):
            st.subheader(t("settings_tags_header"))
            new_tag = st.text_input(t("settings_add_tag"), key="new_tag_input")
            if st.button(t("settings_btn_add_tag"), use_container_width=True) and new_tag:
                manager.add_tag(new_tag)
                st.success(t("settings_tag_added").format(new_tag))
                time.sleep(0.5)
                st.rerun()

            existing_tags = manager.get_tags()
            if existing_tags:
                st.divider()
                tag_to_delete = st.selectbox(t("settings_current_tags"), [""] + existing_tags)
                if tag_to_delete and st.button(f"🗑 {tag_to_delete}", use_container_width=True, type="tertiary"):
                    manager.remove_tag(tag_to_delete)
                    st.success("✅")
                    time.sleep(0.5)
                    st.rerun()


def _inject_global_css():
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
        border: 1px solid #ebedf0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        background-color: #ffffff;
        transition: all 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 6px 16px rgba(0,0,0,0.05);
    }

    div[data-testid="stButton"] button {
        border-radius: 8px;
        font-weight: 500;
        text-transform: none !important;
    }

    div[data-baseweb="select"] > div {
        border-radius: 8px;
    }

    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
    }
    h2 {
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


# --- Main App ---
def main():
    _inject_global_css()
    issues = manager.scan_all_issues()
    render_sidebar()

    state = st.session_state.current_view

    if state == "index":
        render_dashboard(issues)
    elif state == "all_issues":
        render_all_issues(issues)
    elif state == "create":
        render_create_view()
    elif state == "settings":
        render_settings_view()
    elif state == "issue_detail" and st.session_state.selected_issue_id:
        render_issue_view(st.session_state.selected_issue_id)
    else:
        # Fallback
        nav_to("index")


if __name__ == "__main__":
    main()
