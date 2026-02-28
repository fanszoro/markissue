import time
from datetime import datetime

import streamlit as st

from app.i18n import LANG_OPTIONS, t
from app.managers.fs_issue_manager import FileModifiedExternallyError, FileSystemIssueManager

# --- Page Config ---
st.set_page_config(page_title=t("app_title"), page_icon="📁", layout="wide", initial_sidebar_state="expanded")


# --- Initialize Manager & State ---
@st.cache_resource
def get_manager():
    return FileSystemIssueManager()


manager = get_manager()

if "selected_issue_id" not in st.session_state:
    st.session_state.selected_issue_id = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "show_create" not in st.session_state:
    st.session_state.show_create = False
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False


# --- Helper Functions ---
def format_timestamp(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def get_status_color(status):
    colors = {"OPEN": "red", "IN-PROGRESS": "orange", "FIXED": "green", "CLOSED": "gray"}
    return colors.get(status, "blue")


# --- UI Components ---


def render_sidebar(issues):  # noqa: C901
    st.sidebar.title(t("sidebar_title"))

    # Language selector (top of sidebar)
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

    with st.sidebar.expander(t("quick_actions"), expanded=False):
        if st.button(t("btn_new_issue"), use_container_width=True, type="primary"):
            st.session_state.show_create = True
            st.session_state.show_dashboard = False
            st.session_state.show_settings = False
            st.session_state.selected_issue_id = None
            st.session_state.edit_mode = False
            st.rerun()

        if st.button(t("btn_dashboard"), use_container_width=True):
            st.session_state.show_dashboard = True
            st.session_state.show_create = False
            st.session_state.show_settings = False
            st.session_state.selected_issue_id = None
            st.rerun()

        if st.button(t("btn_settings"), use_container_width=True):
            st.session_state.show_settings = True
            st.session_state.show_dashboard = False
            st.session_state.show_create = False
            st.session_state.selected_issue_id = None
            st.rerun()

    st.sidebar.divider()

    st.sidebar.markdown(f"##### {t('filter_search_header')}")
    search_query = st.sidebar.text_input(t("filter_keyword_label"), placeholder=t("filter_keyword_placeholder")).lower()

    with st.sidebar.expander(t("filter_advanced"), expanded=False):
        status_filter = st.multiselect(t("filter_status"), manager.VALID_STATUSES, default=manager.VALID_STATUSES)

        all_tags = manager.get_tags()
        tag_filter = st.multiselect(t("filter_tags"), all_tags)
        tag_or_label = t("filter_tag_or")
        tag_and_label = t("filter_tag_and")
        tag_mode = st.radio(t("filter_tag_mode"), [tag_or_label, tag_and_label], horizontal=True)

        all_users = manager.get_users()
        assignee_filter = st.multiselect(t("filter_assignee"), all_users)

        all_projects = manager.get_projects()
        project_filter = st.multiselect(t("filter_project"), all_projects)

    st.sidebar.markdown(f"##### {t('display_settings')}")
    sort_newest = t("sort_newest")
    sort_oldest = t("sort_oldest")
    sort_updated = t("sort_updated")
    sort_by = st.sidebar.selectbox(t("sort_by"), [sort_newest, sort_oldest, sort_updated])

    st.sidebar.divider()
    batch_mode = st.sidebar.toggle(t("batch_mode"), key="batch_mode_toggle")
    if "batch_selected" not in st.session_state:
        st.session_state.batch_selected = set()

    # 应用过滤与排序
    filtered_issues = []
    for issue in issues:
        # 1. 状态匹配
        if issue["status"].lower() not in [s.lower() for s in status_filter]:
            continue
        # 2. 负责人匹配
        if assignee_filter and issue.get("assignee") not in assignee_filter:
            continue
        # 3. 项目匹配
        if project_filter and issue.get("project") not in project_filter:
            continue
        # 4. 标签匹配
        if tag_filter:
            issue_tags = issue.get("tags", [])
            if tag_mode == tag_or_label:
                if not any(t_item in issue_tags for t_item in tag_filter):
                    continue
            else:  # AND
                if not all(t_item in issue_tags for t_item in tag_filter):
                    continue
        # 5. 搜索匹配
        if search_query:
            if search_query not in issue["id"].lower() and search_query not in issue["title"].lower():
                continue
        filtered_issues.append(issue)

    # 排序
    if sort_by == sort_newest:
        filtered_issues.sort(key=lambda x: x["created_at"], reverse=True)
    elif sort_by == sort_oldest:
        filtered_issues.sort(key=lambda x: x["created_at"], reverse=False)
    elif sort_by == sort_updated:
        filtered_issues.sort(key=lambda x: x["last_modified"], reverse=True)

    # 渲染文件树/列表
    st.sidebar.subheader(f"{t('issue_list')} ({len(filtered_issues)})")

    # Group by status to display nicely
    grouped = {
        s: []
        for s in [
            sf.upper()
            for sf in manager.VALID_STATUSES
            if sf in status_filter or sf.lower() in [f.lower() for f in status_filter]
        ]
    }
    for issue in filtered_issues:
        grouped.get(issue["status"].upper(), []).append(issue)

    for status, status_issues in grouped.items():
        if status_issues:
            is_in_progress = status.upper() == "IN-PROGRESS"
            with st.sidebar.expander(f"📂 {status} ({len(status_issues)})", expanded=is_in_progress):
                for issue in status_issues:
                    btn_label = f"[{issue['type']}] {issue['title']}"

                    # 当前选中的高亮
                    is_selected = st.session_state.selected_issue_id == issue["id"]

                    if batch_mode:
                        is_checked = issue["id"] in st.session_state.batch_selected
                        if st.checkbox(
                            f"{issue['type']} | {issue['title']}", key=f"batch_chk_{issue['id']}", value=is_checked
                        ):
                            st.session_state.batch_selected.add(issue["id"])
                        else:
                            st.session_state.batch_selected.discard(issue["id"])
                    else:
                        if st.button(
                            btn_label,
                            key=f"nav_{issue['id']}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary",
                        ):
                            st.session_state.selected_issue_id = issue["id"]
                            st.session_state.edit_mode = False
                            st.session_state.show_create = False
                            st.session_state.show_dashboard = False
                            st.session_state.show_settings = False
                            st.rerun()


def render_create_view():
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
                st.success(t("create_success", None, new_id))
                st.session_state.show_create = False
                st.session_state.selected_issue_id = new_id
                time.sleep(1)
                st.rerun()
            else:
                st.error(t("create_error_title"))

    with col2:
        if st.button(t("create_btn_cancel")):
            st.session_state.show_create = False
            st.rerun()


@st.dialog(t("conflict_title"))
def show_conflict_dialog(error_msg):
    st.error(error_msg)
    st.write(t("conflict_info"))
    if st.button(t("conflict_btn_reload")):
        st.session_state.edit_mode = False
        st.rerun()


def render_issue_view(issue_id):  # noqa: C901
    try:
        issue = manager.get_issue(issue_id)
    except Exception as e:
        st.error(t("issue_load_error", None, e))
        if st.button(t("issue_btn_back")):
            st.session_state.selected_issue_id = None
            st.rerun()
        return

    # 顶栏区 (操作区)
    col1, col_del, col_edit = st.columns([6, 1, 1])
    with col1:
        st.markdown(f"## `[{issue['type']}]` {issue['title']}")

        tags_html = ""
        current_tags = issue.get("tags", [])
        if current_tags:
            tags_html = " | ".join([f"🏷️ `{tag}`" for tag in current_tags])
            st.caption(
                f"{t('issue_path_label', None, issue['filepath'], format_timestamp(issue['last_modified']))} | {tags_html}"
            )
        else:
            st.caption(t("issue_path_label", None, issue["filepath"], format_timestamp(issue["last_modified"])))

    with col_del:
        if st.checkbox(t("issue_confirm_delete"), key=f"chk_del_{issue_id}"):
            if st.button(t("issue_btn_delete"), type="primary"):
                manager.delete_issue(issue_id)
                st.session_state.selected_issue_id = None
                st.session_state.edit_mode = False
                st.success(t("issue_delete_success"))
                time.sleep(0.8)
                st.rerun()

    with col_edit:
        if st.session_state.edit_mode:
            if st.button(t("issue_btn_cancel_edit")):
                st.session_state.edit_mode = False
                st.rerun()
        else:
            if st.button(t("issue_btn_edit")):
                st.session_state.edit_mode = True
                st.rerun()

    # 状态转移按钮区
    st.write("---")
    cols = st.columns(len(manager.VALID_STATUSES))
    for i, status in enumerate(manager.VALID_STATUSES):
        with cols[i]:
            if status.lower() == issue["status"].lower():
                st.markdown(
                    f"**:{get_status_color(issue['status'].upper())}[{t('issue_current_status', None, status.upper())}]**"
                )
            else:
                if st.button(t("issue_transition_to", None, status.upper()), key=f"mv_{status}"):
                    if manager.change_status(issue_id, status.lower()):
                        st.success(t("issue_moved", None, status))
                        time.sleep(0.5)
                        st.rerun()

    st.write("---")

    col_main, col_meta = st.columns([3, 1])

    # 主体内容区
    with col_main:
        if st.session_state.edit_mode:
            new_content = st.text_area(t("issue_edit_content_label"), value=issue["content"], height=500)
            frontend_mtime = issue["last_modified"]

            if st.button(t("issue_btn_save"), type="primary"):
                try:
                    manager.save_issue_content(issue_id, new_content, frontend_mtime)
                    st.success(t("issue_save_success"))
                    st.session_state.edit_mode = False
                    time.sleep(0.5)
                    st.rerun()
                except FileModifiedExternallyError as e:
                    show_conflict_dialog(str(e))
        else:
            # === 阅读模式 ===
            st.markdown(issue["content"])

            st.divider()

            # --- Quick Attachments ---
            uploaded_file = st.file_uploader(t("issue_upload_label"), key="file_uploader")
            if uploaded_file is not None:
                attachments_dir = manager.base_dir / "attachments"
                attachments_dir.mkdir(exist_ok=True)

                safe_name = f"{int(time.time())}_{uploaded_file.name}"
                file_path = attachments_dir / safe_name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                if uploaded_file.type.startswith("image/"):
                    attachment_md = f"\n\n{t('attach_img_md', None, uploaded_file.name, safe_name)}"
                else:
                    attachment_md = f"\n\n{t('attach_link_md', None, uploaded_file.name, safe_name)}"

                try:
                    manager.save_issue_content(issue_id, issue["content"] + attachment_md, issue["last_modified"])
                    st.success(t("issue_upload_success"))
                    time.sleep(1)
                    st.rerun()
                except FileModifiedExternallyError as e:
                    show_conflict_dialog(str(e))

            # --- Quick Comments ---
            new_comment = st.text_area(t("issue_comment_label"), placeholder=t("issue_comment_placeholder"), height=100)
            if st.button(t("issue_btn_comment")):
                if new_comment.strip():
                    comment_text = f"\n\n{t('comment_header_md', None, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), new_comment.strip())}"
                    try:
                        manager.save_issue_content(issue_id, issue["content"] + comment_text, issue["last_modified"])
                        st.success(t("issue_comment_success"))
                        time.sleep(0.5)
                        st.rerun()
                    except FileModifiedExternallyError as e:
                        show_conflict_dialog(str(e))

    # 元数据侧边栏
    with col_meta:
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
                    if issue.get("priority") in ["Low", "Medium", "High", "Critical"]
                    else 0
                ),
            )

            tags = st.multiselect(t("meta_tags"), available_tags, default=current_tags)

            if st.button(t("meta_btn_update"), key="update_meta"):
                manager.update_metadata(
                    issue_id, {"assignee": assignee, "project": project, "priority": priority, "tags": tags}
                )
                st.toast(t("meta_update_success"))
                time.sleep(0.5)
                st.rerun()


def render_dashboard(issues):
    st.header(t("dashboard_header"))
    st.divider()

    total = len(issues)
    open_count = len([i for i in issues if i["status"].lower() == "open"])
    inprog_count = len([i for i in issues if i["status"].lower() == "in-progress"])
    fixed_count = len([i for i in issues if i["status"].lower() == "fixed"])
    closed_count = len([i for i in issues if i["status"].lower() == "closed"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("dashboard_total"), total)
    col2.metric(t("dashboard_open"), open_count)
    col3.metric(t("dashboard_in_progress"), inprog_count)
    col4.metric(t("dashboard_fixed") + "/" + t("dashboard_closed"), fixed_count + closed_count)

    st.divider()

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader(t("dashboard_by_type"))
        type_counts: dict[str, int] = {}
        for i in issues:
            tp = i.get("type", "unknown").upper()
            type_counts[tp] = type_counts.get(tp, 0) + 1
        if type_counts:
            st.bar_chart(type_counts)
        else:
            st.info(t("dashboard_no_issues"))

    with col_chart2:
        st.subheader(t("dashboard_by_priority"))
        user_counts: dict[str, int] = {}
        for i in issues:
            if i["status"].lower() not in ["fixed", "closed"]:
                u = i.get("assignee", "Unassigned")
                if not u:
                    u = "Unassigned"
                user_counts[u] = user_counts.get(u, 0) + 1
        if user_counts:
            st.bar_chart(user_counts)
        else:
            st.info(t("dashboard_no_issues"))

    st.divider()
    urgent_issues = [
        i
        for i in issues
        if i.get("priority") in ["High", "Critical"] and i["status"].lower() not in ["fixed", "closed"]
    ]
    if urgent_issues:
        for u in urgent_issues:
            assignee_str = u.get("assignee", "—") or "—"
            st.markdown(f"- 🔴 **[{u['type']}]** {u['title']} - *{assignee_str}* (Status: {u['status']})")
    else:
        st.success("✅")


def render_settings_view():
    st.header(t("settings_header"))
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.subheader(t("settings_users_header"))
            new_user = st.text_input(t("settings_add_user"), key="new_user_input")
            if st.button(t("settings_btn_add_user"), use_container_width=True) and new_user:
                manager.add_user(new_user)
                st.success(t("settings_user_added", None, new_user))
                time.sleep(0.5)
                st.rerun()

            existing_users = manager.get_users()
            if existing_users:
                st.divider()
                user_to_delete = st.selectbox(t("settings_current_users"), [""] + existing_users)
                if user_to_delete and st.button(f"🗑 {user_to_delete}", use_container_width=True):
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
                st.success(t("settings_project_added", None, new_project))
                time.sleep(0.5)
                st.rerun()

            existing_projects = manager.get_projects()
            if existing_projects:
                st.divider()
                project_to_delete = st.selectbox(t("settings_current_projects"), [""] + existing_projects)
                if project_to_delete and st.button(f"🗑 {project_to_delete}", use_container_width=True):
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
                st.success(t("settings_tag_added", None, new_tag))
                time.sleep(0.5)
                st.rerun()

            existing_tags = manager.get_tags()
            if existing_tags:
                st.divider()
                tag_to_delete = st.selectbox(t("settings_current_tags"), [""] + existing_tags)
                if tag_to_delete and st.button(f"🗑 {tag_to_delete}", use_container_width=True):
                    manager.remove_tag(tag_to_delete)
                    st.success("✅")
                    time.sleep(0.5)
                    st.rerun()


def render_batch_action_bar():
    selected_ids = st.session_state.get("batch_selected", set())
    if not selected_ids:
        st.info("💡")
        return

    st.subheader(t("batch_selected", None, len(selected_ids)))

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            new_status = st.selectbox(t("batch_status_label"), ["--"] + manager.VALID_STATUSES)
        with col2:
            all_users = manager.get_users()
            new_assignee = st.selectbox(t("meta_assignee"), ["--"] + all_users)
        with col3:
            all_projects = manager.get_projects()
            new_project = st.selectbox(t("meta_project"), ["--"] + all_projects)
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(t("batch_btn_apply"), type="primary", use_container_width=True):
                updates = {}
                if new_assignee != "--":
                    updates["assignee"] = new_assignee
                if new_project != "--":
                    updates["project"] = new_project

                selected_list = list(selected_ids)
                if updates:
                    manager.batch_update_metadata(selected_list, updates)

                if new_status != "--":
                    manager.batch_change_status(selected_list, new_status)

                st.success(t("batch_success"))
                st.session_state.batch_selected = set()
                time.sleep(1)
                st.rerun()

    if st.button(t("batch_btn_clear"), use_container_width=True):
        st.session_state.batch_selected = set()
        st.rerun()


def render_index_page(issues):
    st.title(f"📁 {t('index_header')}")
    st.markdown("---")

    total = len(issues)
    open_count = len([i for i in issues if i["status"].lower() == "open"])
    inprog_count = len([i for i in issues if i["status"].lower() == "in-progress"])

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric(t("index_metric_total"), total)
    with col_stat2:
        st.metric(t("index_metric_open"), open_count)
    with col_stat3:
        st.metric(t("index_metric_progress"), inprog_count)

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader(t("index_recent_issues"))
        recent_issues = sorted(issues, key=lambda x: x["last_modified"], reverse=True)[:10]

        if not recent_issues:
            st.info(t("index_no_issues"))
        else:
            for issue in recent_issues:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**[{issue['type']}]** {issue['title']}")
                        assignee_display = issue.get("assignee") or "—"
                        st.caption(f"{format_timestamp(issue['last_modified'])} | {assignee_display}")
                    with c2:
                        if st.button("🔍", key=f"index_{issue['id']}", use_container_width=True):
                            st.session_state.selected_issue_id = issue["id"]
                            st.session_state.edit_mode = False
                            st.rerun()

    with col_right:
        st.subheader(t("index_quick_start"))
        st.info(t("index_quick_start_content"))

        st.divider()
        if st.container(border=True).button(t("index_btn_goto_dashboard"), use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()


# --- Main App ---
def main():
    issues = manager.scan_all_issues()
    render_sidebar(issues)

    # 优先处理批量操作视图
    if st.session_state.get("batch_mode_toggle", False):
        render_batch_action_bar()
        return

    if getattr(st.session_state, "show_dashboard", False):
        render_dashboard(issues)
    elif getattr(st.session_state, "show_settings", False):
        render_settings_view()
    elif st.session_state.show_create:
        render_create_view()
    elif st.session_state.selected_issue_id:
        render_issue_view(st.session_state.selected_issue_id)
    else:
        render_index_page(issues)


if __name__ == "__main__":
    main()
