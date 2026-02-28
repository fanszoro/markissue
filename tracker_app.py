import time
from datetime import datetime

import streamlit as st

from app.managers.fs_issue_manager import FileModifiedExternallyError, FileSystemIssueManager

# --- Page Config ---
st.set_page_config(
    page_title="MarkIssue (File System)", page_icon="📁", layout="wide", initial_sidebar_state="expanded"
)


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
    st.sidebar.title("📁 MarkIssue Tracker")

    with st.sidebar.expander("🛠️ 快捷功能", expanded=False):
        if st.button("➕ 新建问题单", use_container_width=True, type="primary"):
            st.session_state.show_create = True
            st.session_state.show_dashboard = False
            st.session_state.show_settings = False
            st.session_state.selected_issue_id = None
            st.session_state.edit_mode = False
            st.rerun()

        if st.button("📊 统计看板", use_container_width=True):
            st.session_state.show_dashboard = True
            st.session_state.show_create = False
            st.session_state.show_settings = False
            st.session_state.selected_issue_id = None
            st.rerun()

        if st.button("⚙️ 配置管理", use_container_width=True):
            st.session_state.show_settings = True
            st.session_state.show_dashboard = False
            st.session_state.show_create = False
            st.session_state.selected_issue_id = None
            st.rerun()

    st.sidebar.divider()

    st.sidebar.markdown("##### 过滤与搜索")
    search_query = st.sidebar.text_input("关键字搜索", placeholder="输入标题或ID...").lower()

    with st.sidebar.expander("🔍 高级过滤", expanded=False):
        status_filter = st.multiselect("状态", manager.VALID_STATUSES, default=manager.VALID_STATUSES)

        all_tags = manager.get_tags()
        tag_filter = st.multiselect("标签", all_tags)
        tag_mode = st.radio("标签匹配模式", ["任一 (OR)", "全部 (AND)"], horizontal=True)

        all_users = manager.get_users()
        assignee_filter = st.multiselect("负责人", all_users)

        all_projects = manager.get_projects()
        project_filter = st.multiselect("项目", all_projects)

    st.sidebar.markdown("##### 显示设置")
    sort_by = st.sidebar.selectbox("排序策略", ["最新创建", "最新更新", "最老创建"])

    st.sidebar.divider()
    batch_mode = st.sidebar.toggle("⚡ 批量操作模式", key="batch_mode_toggle")
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
            if tag_mode == "任一 (OR)":
                if not any(t in issue_tags for t in tag_filter):
                    continue
            else:  # AND
                if not all(t in issue_tags for t in tag_filter):
                    continue
        # 5. 搜索匹配
        if search_query:
            if search_query not in issue["id"].lower() and search_query not in issue["title"].lower():
                continue
        filtered_issues.append(issue)

    # 排序
    if sort_by == "最新创建":
        filtered_issues.sort(key=lambda x: x["created_at"], reverse=True)
    elif sort_by == "最老创建":
        filtered_issues.sort(key=lambda x: x["created_at"], reverse=False)
    elif sort_by == "最新更新":
        filtered_issues.sort(key=lambda x: x["last_modified"], reverse=True)

    # 渲染文件树/列表
    st.sidebar.subheader(f"问题列表 ({len(filtered_issues)})")

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
    st.header("✨ 新建问题单")

    col1, col2 = st.columns([1, 1])
    with col1:
        issue_type = st.selectbox("问题类型", ["bug", "fea", "opt", "doc", "task"])
    with col2:
        title = st.text_input("简述标题 (将作为文件名一部分)", max_chars=50)

    content = st.text_area("详细描述 (Markdown格式)", height=400)

    # 额外元数据
    with st.expander("附加属性"):
        users = [""] + manager.get_users()
        projects = [""] + manager.get_projects()
        available_tags = manager.get_tags()

        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            assignee = st.selectbox("处理人", users)
        with col_meta2:
            project = st.selectbox("归属项目", projects)

        priority = st.selectbox("优先级", ["Low", "Medium", "High", "Critical"])
        selected_tags = st.multiselect("标签", available_tags)

    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        if st.button("💾 创建并保存", type="primary"):
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
                st.success(f"问题单 {new_id} 创建成功！")
                st.session_state.show_create = False
                st.session_state.selected_issue_id = new_id
                time.sleep(1)
                st.rerun()
            else:
                st.error("请输入标题")

    with col2:
        if st.button("取消"):
            st.session_state.show_create = False
            st.rerun()


@st.dialog("⚠ 文件冲突警告")
def show_conflict_dialog(error_msg):
    st.error(error_msg)
    st.write("此问题可能由于其他人正在编辑同一个文件，或者后台发生变动引起。")
    if st.button("重新加载最新内容"):
        st.session_state.edit_mode = False
        st.rerun()


def render_issue_view(issue_id):  # noqa: C901
    try:
        issue = manager.get_issue(issue_id)
    except Exception as e:
        st.error(f"无法加载问题单: {e}")
        if st.button("返回列表"):
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
            tags_html = " | ".join([f"🏷️ `{t}`" for t in current_tags])
            st.caption(
                f"路径: `{issue['filepath']}` | 最后修改: {format_timestamp(issue['last_modified'])} | {tags_html}"
            )
        else:
            st.caption(f"路径: `{issue['filepath']}` | 最后修改: {format_timestamp(issue['last_modified'])}")

    with col_del:
        if st.checkbox("确认删除", key=f"chk_del_{issue_id}"):
            if st.button("🗑 永久删除", type="primary"):
                manager.delete_issue(issue_id)
                st.session_state.selected_issue_id = None
                st.session_state.edit_mode = False
                st.success("已彻底删除文件！")
                time.sleep(0.8)
                st.rerun()

    with col_edit:
        if st.session_state.edit_mode:
            if st.button("取消编辑"):
                st.session_state.edit_mode = False
                st.rerun()
        else:
            if st.button("✏️ 编辑内容"):
                st.session_state.edit_mode = True
                st.rerun()

    # 状态转移按钮区
    st.write("---")
    cols = st.columns(len(manager.VALID_STATUSES))
    for i, status in enumerate(manager.VALID_STATUSES):
        with cols[i]:
            if status.lower() == issue["status"].lower():
                st.markdown(f"**:{get_status_color(issue['status'].upper())}[当前状态: {status.upper()}]**")
            else:
                if st.button(f"流转到 ➔ {status.upper()}", key=f"mv_{status}"):
                    if manager.change_status(issue_id, status.lower()):
                        st.success(f"已移动到 {status} 目录")
                        time.sleep(0.5)
                        st.rerun()

    st.write("---")

    col_main, col_meta = st.columns([3, 1])

    # 主体内容区
    with col_main:
        if st.session_state.edit_mode:
            # === 编辑模式 (乐观锁校验) ===
            new_content = st.text_area("Markdown 内容", value=issue["content"], height=500)

            # 使用一个隐藏的 key 来存当时读取的时间戳
            frontend_mtime = issue["last_modified"]

            if st.button("💾 保存更改", type="primary"):
                try:
                    manager.save_issue_content(issue_id, new_content, frontend_mtime)
                    st.success("保存成功！")
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
            uploaded_file = st.file_uploader("📎 上传附件到此问题单 (自动追加到文末)", key="file_uploader")
            if uploaded_file is not None:
                attachments_dir = manager.base_dir / "attachments"
                attachments_dir.mkdir(exist_ok=True)

                safe_name = f"{int(time.time())}_{uploaded_file.name}"
                file_path = attachments_dir / safe_name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # 自动生成 Markdown 相对链接追加到正文
                attachment_md = f"\n\n📎 **附件**: [{uploaded_file.name}](../../attachments/{safe_name})"
                if uploaded_file.type.startswith("image/"):
                    attachment_md = f"\n\n📷 **图片附件**:\n![{uploaded_file.name}](../../attachments/{safe_name})"

                try:
                    manager.save_issue_content(issue_id, issue["content"] + attachment_md, issue["last_modified"])
                    st.success("附件已上传并追加到正文！")
                    time.sleep(1)
                    st.rerun()
                except FileModifiedExternallyError as e:
                    show_conflict_dialog(str(e))

            # --- Quick Comments ---
            new_comment = st.text_area("💬 追加评论", placeholder="输入进度更新或评论...", height=100)
            if st.button("发送评论"):
                if new_comment.strip():
                    comment_text = (
                        f"\n\n---\n**💬 追评 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]**:\n{new_comment.strip()}"
                    )
                    try:
                        manager.save_issue_content(issue_id, issue["content"] + comment_text, issue["last_modified"])
                        st.success("评论已追加！")
                        time.sleep(0.5)
                        st.rerun()
                    except FileModifiedExternallyError as e:
                        show_conflict_dialog(str(e))

    # 元数据侧边栏
    with col_meta:
        with st.container(border=True):
            st.markdown("### 🏷️ 属性")

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
            for t in current_tags:
                if t not in available_tags:
                    available_tags.append(t)

            assignee = st.selectbox(
                "处理人", users, index=users.index(current_assignee) if current_assignee in users else 0
            )
            project = st.selectbox(
                "归属项目", projects, index=projects.index(current_project) if current_project in projects else 0
            )

            priority = st.selectbox(
                "优先级",
                ["Low", "Medium", "High", "Critical"],
                index=(
                    ["Low", "Medium", "High", "Critical"].index(issue.get("priority", "Low"))
                    if issue.get("priority") in ["Low", "Medium", "High", "Critical"]
                    else 0
                ),
            )

            tags = st.multiselect("标签", available_tags, default=current_tags)

            if st.button("更新属性", key="update_meta"):
                manager.update_metadata(
                    issue_id, {"assignee": assignee, "project": project, "priority": priority, "tags": tags}
                )
                st.toast("属性已更新字典")
                time.sleep(0.5)
                st.rerun()


def render_dashboard(issues):
    st.header("📊 全景数据看板")
    st.divider()

    total = len(issues)
    open_count = len([i for i in issues if i["status"].lower() == "open"])
    inprog_count = len([i for i in issues if i["status"].lower() == "in-progress"])
    fixed_count = len([i for i in issues if i["status"].lower() == "fixed"])
    closed_count = len([i for i in issues if i["status"].lower() == "closed"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总计数量", total)
    col2.metric("Open", open_count)
    col3.metric("In-Progress", inprog_count)
    col4.metric("Fixed/Closed", fixed_count + closed_count)

    st.divider()

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("按类型分布")
        type_counts = {}
        for i in issues:
            t = i.get("type", "unknown").upper()
            type_counts[t] = type_counts.get(t, 0) + 1
        if type_counts:
            st.bar_chart(type_counts)
        else:
            st.info("暂无数据")

    with col_chart2:
        st.subheader("未完结按处理人分布")
        user_counts = {}
        for i in issues:
            if i["status"].lower() not in ["fixed", "closed"]:
                u = i.get("assignee", "Unassigned")
                if not u:
                    u = "Unassigned"
                user_counts[u] = user_counts.get(u, 0) + 1
        if user_counts:
            st.bar_chart(user_counts)
        else:
            st.info("暂无数据")

    st.divider()
    st.subheader("未完结的高优先级问题 (High / Critical)")
    urgent_issues = [
        i
        for i in issues
        if i.get("priority") in ["High", "Critical"] and i["status"].lower() not in ["fixed", "closed"]
    ]
    if urgent_issues:
        for u in urgent_issues:
            st.markdown(
                f"- 🔴 **[{u['type']}]** {u['title']} - *处理人: {u.get('assignee', '暂无')}* (Status: {u['status']})"
            )
    else:
        st.success("目前没有未完结的高优先级问题！")


def render_settings_view():
    st.header("⚙️ 配置管理")
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.subheader("👤 用户管理")
            new_user = st.text_input("新建用户", key="new_user_input")
            if st.button("添加用户", use_container_width=True) and new_user:
                manager.add_user(new_user)
                st.success(f"已添加用户: {new_user}")
                time.sleep(0.5)
                st.rerun()

            existing_users = manager.get_users()
            if existing_users:
                st.divider()
                user_to_delete = st.selectbox("选择要删除的用户", [""] + existing_users)
                if user_to_delete and st.button(f"🗑 删除 {user_to_delete}", use_container_width=True):
                    manager.remove_user(user_to_delete)
                    st.success("已删除")
                    time.sleep(0.5)
                    st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("📁 项目管理")
            new_project = st.text_input("新建项目", key="new_project_input")
            if st.button("添加项目", use_container_width=True) and new_project:
                manager.add_project(new_project)
                st.success(f"已添加项目: {new_project}")
                time.sleep(0.5)
                st.rerun()

            existing_projects = manager.get_projects()
            if existing_projects:
                st.divider()
                project_to_delete = st.selectbox("选择要删除的项目", [""] + existing_projects)
                if project_to_delete and st.button(f"🗑 删除项目: {project_to_delete}", use_container_width=True):
                    manager.remove_project(project_to_delete)
                    st.success("已删除")
                    time.sleep(0.5)
                    st.rerun()

    with col3:
        with st.container(border=True):
            st.subheader("🏷️ 标签管理")
            new_tag = st.text_input("新建标签", key="new_tag_input")
            if st.button("添加标签", use_container_width=True) and new_tag:
                manager.add_tag(new_tag)
                st.success(f"已添加标签: {new_tag}")
                time.sleep(0.5)
                st.rerun()

            existing_tags = manager.get_tags()
            if existing_tags:
                st.divider()
                tag_to_delete = st.selectbox("选择要删除的标签", [""] + existing_tags)
                if tag_to_delete and st.button(f"🗑 删除标签: {tag_to_delete}", use_container_width=True):
                    manager.remove_tag(tag_to_delete)
                    st.success("已删除")
                    time.sleep(0.5)
                    st.rerun()


def render_batch_action_bar():
    selected_ids = st.session_state.get("batch_selected", set())
    if not selected_ids:
        st.info("💡 请在左侧勾选需要操作的问题单。")
        return

    st.subheader(f"⚡ 批量操作 ({len(selected_ids)} 个已选)")

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            new_status = st.selectbox("变更状态", ["-- 不变 --"] + manager.VALID_STATUSES)
        with col2:
            all_users = manager.get_users()
            new_assignee = st.selectbox("变更负责人", ["-- 不变 --"] + all_users)
        with col3:
            all_projects = manager.get_projects()
            new_project = st.selectbox("变更项目", ["-- 不变 --"] + all_projects)
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 执行批量更新", type="primary", use_container_width=True):
                updates = {}
                if new_assignee != "-- 不变 --":
                    updates["assignee"] = new_assignee
                if new_project != "-- 不变 --":
                    updates["project"] = new_project

                selected_list = list(selected_ids)
                if updates:
                    manager.batch_update_metadata(selected_list, updates)

                if new_status != "-- 不变 --":
                    manager.batch_change_status(selected_list, new_status)

                st.success(f"成功更新 {len(selected_ids)} 个问题单！")
                st.session_state.batch_selected = set()
                time.sleep(1)
                st.rerun()

    if st.button("🧹 清空选择", use_container_width=True):
        st.session_state.batch_selected = set()
        st.rerun()


def render_index_page(issues):
    st.title("📁 MarkIssue 概览")
    st.markdown("---")

    total = len(issues)
    open_count = len([i for i in issues if i["status"].lower() == "open"])
    inprog_count = len([i for i in issues if i["status"].lower() == "in-progress"])

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("总计问题单", total)
    with col_stat2:
        st.metric("待处理 (Open)", open_count)
    with col_stat3:
        st.metric("处理中 (In-Progress)", inprog_count)

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🕑 最近更新 (Recently Updated)")
        recent_issues = sorted(issues, key=lambda x: x["last_modified"], reverse=True)[:10]

        if not recent_issues:
            st.info("暂无记录")
        else:
            for issue in recent_issues:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**[{issue['type']}]** {issue['title']}")
                        st.caption(
                            f"修改时间: {format_timestamp(issue['last_modified'])} | 负责人: {issue.get('assignee', '未指派')}"
                        )
                    with c2:
                        if st.button("查看详情", key=f"index_{issue['id']}", use_container_width=True):
                            st.session_state.selected_issue_id = issue["id"]
                            st.session_state.edit_mode = False
                            st.rerun()

    with col_right:
        st.subheader("💡 快速上手")
        st.info(
            """
        - **新建**: 点击左侧折叠区 `➕` 按钮开始创建。
        - **搜索**: 使用侧边栏输入框进行关键字查询。
        - **状态**: 点击流转按钮，文件会自动移动到相应目录下。
        - **AI 友好**: 所有的内容都以 Markdown 存储在 `LocalStorage/issues` 下。
        """
        )

        st.divider()
        if st.container(border=True).button("📊 前往数据大屏", use_container_width=True):
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
