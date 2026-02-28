import streamlit as st
from datetime import datetime
import time

from app.managers.fs_issue_manager import FileSystemIssueManager, FileModifiedExternallyError

# --- Page Config ---
st.set_page_config(
    page_title="MarkIssue (File System)",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Manager & State ---
@st.cache_resource
def get_manager():
    return FileSystemIssueManager()

manager = get_manager()

if 'selected_issue_id' not in st.session_state:
    st.session_state.selected_issue_id = None
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'show_create' not in st.session_state:
    st.session_state.show_create = False
if 'show_dashboard' not in st.session_state:
    st.session_state.show_dashboard = False
if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False

# --- Helper Functions ---
def format_timestamp(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def get_status_color(status):
    colors = {
        "OPEN": "red",
        "IN-PROGRESS": "orange",
        "FIXED": "green",
        "CLOSED": "gray"
    }
    return colors.get(status, "blue")

# --- UI Components ---

def render_sidebar(issues):
    st.sidebar.title("📁 MarkIssue Tracker")
    
    if st.sidebar.button("➕ 新建问题单", use_container_width=True, type="primary"):
        st.session_state.show_create = True
        st.session_state.show_dashboard = False
        st.session_state.show_settings = False
        st.session_state.selected_issue_id = None
        st.session_state.edit_mode = False
        st.rerun()
        
    if st.sidebar.button("📊 统计看板", use_container_width=True):
        st.session_state.show_dashboard = True
        st.session_state.show_create = False
        st.session_state.show_settings = False
        st.session_state.selected_issue_id = None
        st.rerun()

    if st.sidebar.button("⚙️ 配置管理", use_container_width=True):
        st.session_state.show_settings = True
        st.session_state.show_dashboard = False
        st.session_state.show_create = False
        st.session_state.selected_issue_id = None
        st.rerun()
        
    st.sidebar.divider()
    
    # 过滤器与搜索
    search_query = st.sidebar.text_input("关键字搜索 (按回车应用)", placeholder="输入标题或ID...").lower()
    
    st.sidebar.markdown("##### 显示设置")
    sort_by = st.sidebar.selectbox("排序策略", ["最新创建", "最新更新", "最老创建"])
    status_filter = st.sidebar.multiselect("包含状态", manager.VALID_STATUSES, default=manager.VALID_STATUSES)

    # 应用过滤与排序
    filtered_issues = []
    for issue in issues:
        # 1. 状态匹配
        if issue['status'].lower() not in [s.lower() for s in status_filter]:
            continue
        # 2. 搜索匹配
        if search_query:
            if search_query not in issue['id'].lower() and search_query not in issue['title'].lower():
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
    grouped = {s: [] for s in [sf.upper() for sf in manager.VALID_STATUSES if sf in status_filter or sf.lower() in [f.lower() for f in status_filter]]}
    for issue in filtered_issues:
        grouped.get(issue['status'].upper(), []).append(issue)

    for status, status_issues in grouped.items():
        if status_issues:
            is_in_progress = (status.upper() == "IN-PROGRESS")
            with st.sidebar.expander(f"📂 {status} ({len(status_issues)})", expanded=is_in_progress):
                for issue in status_issues:
                    btn_label = f"[{issue['type']}] {issue['title']}"
                    
                    # 当前选中的高亮
                    is_selected = st.session_state.selected_issue_id == issue['id']
                    
                    if st.button(
                        btn_label, 
                        key=f"nav_{issue['id']}", 
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.selected_issue_id = issue['id']
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
                if assignee: extra["assignee"] = assignee
                if project: extra["project"] = project
                if priority: extra["priority"] = priority
                if selected_tags: extra["tags"] = selected_tags
                
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

def render_issue_view(issue_id):
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
        current_tags = issue.get('tags', [])
        if current_tags:
            tags_html = " | ".join([f"🏷️ `{t}`" for t in current_tags])
            st.caption(f"路径: `{issue['filepath']}` | 最后修改: {format_timestamp(issue['last_modified'])} | {tags_html}")
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
            if status.lower() == issue['status'].lower():
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
            new_content = st.text_area("Markdown 内容", value=issue['content'], height=500)
            
            # 使用一个隐藏的 key 来存当时读取的时间戳
            frontend_mtime = issue['last_modified']
            
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
            st.markdown(issue['content'])
            
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
                if uploaded_file.type.startswith('image/'):
                    attachment_md = f"\n\n📷 **图片附件**:\n![{uploaded_file.name}](../../attachments/{safe_name})"
                    
                try:
                    manager.save_issue_content(issue_id, issue['content'] + attachment_md, issue['last_modified'])
                    st.success("附件已上传并追加到正文！")
                    time.sleep(1)
                    st.rerun()
                except FileModifiedExternallyError as e:
                    show_conflict_dialog(str(e))
                
            # --- Quick Comments ---
            new_comment = st.text_area("💬 追加评论", placeholder="输入进度更新或评论...", height=100)
            if st.button("发送评论"):
                if new_comment.strip():
                    comment_text = f"\n\n---\n**💬 追评 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]**:\n{new_comment.strip()}"
                    try:
                        manager.save_issue_content(issue_id, issue['content'] + comment_text, issue['last_modified'])
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
            current_assignee = issue.get('assignee', '')
            if current_assignee and current_assignee not in users:
                users.append(current_assignee)
                
            projects = [""] + manager.get_projects()
            current_project = issue.get('project', '')
            if current_project and current_project not in projects:
                projects.append(current_project)
                
            available_tags = manager.get_tags()
            current_tags = issue.get('tags', [])
            for t in current_tags:
                if t not in available_tags:
                    available_tags.append(t)
                
            assignee = st.selectbox("处理人", users, index=users.index(current_assignee) if current_assignee in users else 0)
            project = st.selectbox("归属项目", projects, index=projects.index(current_project) if current_project in projects else 0)
            
            priority = st.selectbox("优先级", ["Low", "Medium", "High", "Critical"], 
                                    index=["Low", "Medium", "High", "Critical"].index(issue.get('priority', 'Low')) if issue.get('priority') in ["Low", "Medium", "High", "Critical"] else 0)
            
            tags = st.multiselect("标签", available_tags, default=current_tags)
            
            if st.button("更新属性", key="update_meta"):
                manager.update_metadata(issue_id, {"assignee": assignee, "project": project, "priority": priority, "tags": tags})
                st.toast("属性已更新字典")
                time.sleep(0.5)
                st.rerun()

def render_dashboard(issues):
    st.header("📊 全景数据看板")
    st.divider()
    
    total = len(issues)
    open_count = len([i for i in issues if i['status'].lower() == 'open'])
    inprog_count = len([i for i in issues if i['status'].lower() == 'in-progress'])
    fixed_count = len([i for i in issues if i['status'].lower() == 'fixed'])
    closed_count = len([i for i in issues if i['status'].lower() == 'closed'])
    
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
            t = i.get('type', 'unknown').upper()
            type_counts[t] = type_counts.get(t, 0) + 1
        if type_counts:
            st.bar_chart(type_counts)
        else:
            st.info("暂无数据")
        
    with col_chart2:
        st.subheader("未完结按处理人分布")
        user_counts = {}
        for i in issues:
            if i['status'].lower() not in ['fixed', 'closed']:
                u = i.get('assignee', 'Unassigned')
                if not u: u = 'Unassigned'
                user_counts[u] = user_counts.get(u, 0) + 1
        if user_counts:
            st.bar_chart(user_counts)
        else:
            st.info("暂无数据")
            
    st.divider()
    st.subheader("未完结的高优先级问题 (High / Critical)")
    urgent_issues = [i for i in issues if i.get('priority') in ['High', 'Critical'] and i['status'].lower() not in ['fixed', 'closed']]
    if urgent_issues:
        for u in urgent_issues:
            st.markdown(f"- 🔴 **[{u['type']}]** {u['title']} - *处理人: {u.get('assignee', '暂无')}* (Status: {u['status']})")
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

# --- Main App ---
def main():
    issues = manager.scan_all_issues()
    render_sidebar(issues)
    
    if getattr(st.session_state, 'show_dashboard', False):
        render_dashboard(issues)
    elif getattr(st.session_state, 'show_settings', False):
        render_settings_view()
    elif st.session_state.show_create:
        render_create_view()
    elif st.session_state.selected_issue_id:
        render_issue_view(st.session_state.selected_issue_id)
    else:
        st.info("👈 请从左侧选择一个操作。")
        st.write("当前总计追踪的问题单数量: ", len(issues))

if __name__ == "__main__":
    main()
