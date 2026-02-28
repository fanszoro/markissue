"""
app/i18n.py – Lightweight internationalization for MarkIssue Tracker.

Usage:
    from app.i18n import t, LANG_OPTIONS
    # Set language once (in sidebar)
    t("sidebar_title")           → "📁 MarkIssue Tracker"
    t("sidebar_title", "en")     → "📁 MarkIssue Tracker"
"""

LANG_OPTIONS = {"中文 (Chinese)": "zh", "English": "en"}

_STRINGS: dict[str, dict[str, str]] = {
    # --- App Shell ---
    "app_title": {"zh": "MarkIssue (文件系统)", "en": "MarkIssue (File System)"},
    "sidebar_title": {"zh": "📁 MarkIssue Tracker", "en": "📁 MarkIssue Tracker"},
    "lang_selector_label": {"zh": "语言 / Language", "en": "Language / 语言"},
    # --- Sidebar Quick Actions ---
    "quick_actions": {"zh": "🛠️ 快捷功能", "en": "🛠️ Quick Actions"},
    "btn_new_issue": {"zh": "➕ 新建问题单", "en": "➕ New Issue"},
    "btn_dashboard": {"zh": "📊 统计看板", "en": "📊 Dashboard"},
    "btn_settings": {"zh": "⚙️ 配置管理", "en": "⚙️ Settings"},
    # --- Sidebar Filter ---
    "filter_search_header": {"zh": "🔍 过滤与搜索", "en": "🔍 Filter & Search"},
    "filter_keyword_label": {"zh": "关键字搜索", "en": "Keyword Search"},
    "filter_keyword_placeholder": {"zh": "输入标题或ID...", "en": "Enter title or ID..."},
    "filter_advanced": {"zh": "🔍 高级过滤", "en": "🔍 Advanced Filters"},
    "filter_status": {"zh": "🚥 状态", "en": "🚥 Status"},
    "filter_tags": {"zh": "🏷️ 标签", "en": "🏷️ Tags"},
    "filter_tag_mode": {"zh": "标签匹配模式", "en": "Tag Match Mode"},
    "filter_tag_or": {"zh": "任一 (OR)", "en": "Any (OR)"},
    "filter_tag_and": {"zh": "全部 (AND)", "en": "All (AND)"},
    "filter_assignee": {"zh": "👤 负责人", "en": "👤 Assignee"},
    "filter_project": {"zh": "📁 项目", "en": "📁 Project"},
    # --- Sidebar Sort/Display ---
    "display_settings": {"zh": "显示设置", "en": "Display"},
    "sort_by": {"zh": "↕️ 排序策略", "en": "↕️ Sort By"},
    "sort_newest": {"zh": "最新创建", "en": "Newest Created"},
    "sort_oldest": {"zh": "最老创建", "en": "Oldest Created"},
    "sort_updated": {"zh": "最新更新", "en": "Last Updated"},
    "batch_mode": {"zh": "⚡ 批量操作模式", "en": "⚡ Batch Mode"},
    "issue_list": {"zh": "问题列表", "en": "Issue List"},
    # --- Create View ---
    "create_header": {"zh": "✨ 新建问题单", "en": "✨ Create New Issue"},
    "create_type": {"zh": "📌 问题类型", "en": "📌 Issue Type"},
    "create_title": {"zh": "📝 简述标题 (将作为文件名一部分)", "en": "📝 Brief Title (used as filename)"},
    "create_content": {"zh": "✍️ 详细描述 (Markdown格式)", "en": "✍️ Description (Markdown)"},
    "create_extra": {"zh": "🎭 附加属性", "en": "🎭 Additional Attributes"},
    "create_btn_submit": {"zh": "💾 创建并保存", "en": "💾 Create & Save"},
    "create_btn_cancel": {"zh": "取消", "en": "Cancel"},
    "create_success": {"zh": "问题单 {} 创建成功！", "en": "Issue {} created successfully!"},
    "create_error_title": {"zh": "请输入标题", "en": "Please enter a title"},
    # --- Issue View ---
    "issue_load_error": {"zh": "无法加载问题单: {}", "en": "Failed to load issue: {}"},
    "issue_btn_back": {"zh": "返回列表", "en": "Back to List"},
    "issue_path_label": {"zh": "📍 路径: `{}` | 🕒 最后修改: {}", "en": "📍 Path: `{}` | 🕒 Last modified: {}"},
    "issue_confirm_delete": {"zh": "确认删除", "en": "Confirm Delete"},
    "issue_btn_delete": {"zh": "🗑 永久删除", "en": "🗑 Delete"},
    "issue_delete_success": {"zh": "已彻底删除文件！", "en": "File deleted successfully!"},
    "issue_btn_cancel_edit": {"zh": "取消编辑", "en": "Cancel Edit"},
    "issue_btn_edit": {"zh": "✏️ 编辑内容", "en": "✏️ Edit"},
    "issue_current_status": {"zh": "当前状态: {}", "en": "Current Status: {}"},
    "issue_transition_to": {"zh": "流转至 {}", "en": "Move to {}"},
    "issue_moved": {"zh": "已流转至 {}", "en": "Moved to {}"},
    "issue_edit_content_label": {"zh": "Markdown 内容", "en": "Markdown Content"},
    "issue_btn_save": {"zh": "💾 保存更改", "en": "💾 Save Changes"},
    "issue_save_success": {"zh": "保存成功！", "en": "Saved successfully!"},
    "issue_upload_label": {
        "zh": "📎 上传附件到此问题单 (自动追加到文末)",
        "en": "📎 Upload Attachment (appended to content)",
    },
    "issue_upload_success": {"zh": "附件已上传并追加到正文！", "en": "Attachment uploaded and appended!"},
    "issue_comment_label": {"zh": "💬 追加评论", "en": "💬 Add Comment"},
    "issue_comment_placeholder": {"zh": "输入进度更新或评论...", "en": "Enter a progress update or comment..."},
    "issue_btn_comment": {"zh": "发送评论", "en": "Post Comment"},
    "issue_comment_success": {"zh": "评论已追加！", "en": "Comment appended!"},
    # --- Meta Panel ---
    "meta_title": {"zh": "### 🏷️ 属性", "en": "### 🏷️ Properties"},
    "meta_assignee": {"zh": "👤 处理人", "en": "👤 Assignee"},
    "meta_project": {"zh": "📁 归属项目", "en": "📁 Project"},
    "meta_priority": {"zh": "🔥 优先级", "en": "🔥 Priority"},
    "meta_tags": {"zh": "🏷️ 标签", "en": "🏷️ Tags"},
    "meta_btn_update": {"zh": "🔄 更新属性", "en": "🔄 Update Properties"},
    "meta_update_success": {"zh": "属性已更新", "en": "Properties updated"},
    # --- Conflict Dialog ---
    "conflict_title": {"zh": "⚠ 文件冲突警告", "en": "⚠ File Conflict Warning"},
    "conflict_info": {
        "zh": "此问题可能由于其他人正在编辑同一个文件，或者后台发生变动引起。",
        "en": "This may be caused by another user editing the same file, or a background change.",
    },
    "conflict_btn_reload": {"zh": "重新加载最新内容", "en": "Reload Latest Content"},
    # --- Dashboard ---
    "dashboard_header": {"zh": "统计看板", "en": "Dashboard"},
    "dashboard_total": {"zh": "问题总数", "en": "Total Issues"},
    "dashboard_open": {"zh": "待处理", "en": "Open"},
    "dashboard_in_progress": {"zh": "处理中", "en": "In Progress"},
    "dashboard_fixed": {"zh": "已修复", "en": "Fixed"},
    "dashboard_closed": {"zh": "已关闭", "en": "Closed"},
    "dashboard_by_priority": {"zh": "🎯 按优先级分布", "en": "🎯 By Priority"},
    "dashboard_by_type": {"zh": "📊 分类占比", "en": "📊 Type Distribution"},
    "dashboard_recent": {"zh": "最近活跃", "en": "Recent Activity"},
    "dashboard_no_issues": {"zh": "暂无问题单", "en": "No issues yet"},
    # --- Batch ---
    "batch_header": {"zh": "⚡ 批量操作", "en": "⚡ Batch Operations"},
    "batch_selected": {"zh": "已选 {} 个问题", "en": "{} issues selected"},
    "batch_status_label": {"zh": "更新状态", "en": "Update Status"},
    "batch_btn_apply": {"zh": "执行应用 (已选中 {} 个)", "en": "Apply ({} selected)"},
    "batch_success": {"zh": "批量更新应用成功！", "en": "Batch update applied successfully!"},
    "batch_btn_clear": {"zh": "清空选择", "en": "Clear Selection"},
    "batch_btn_exit": {"zh": "退出批量模式", "en": "Exit Batch Mode"},
    # --- Index Page ---
    "index_header": {"zh": "✨ 欢迎使用 MarkIssue 追踪系统", "en": "✨ Welcome to MarkIssue Tracker"},
    "index_metric_total": {"zh": "📦 总问题数", "en": "📦 Total Issues"},
    "index_metric_open": {"zh": "待处理", "en": "Open"},
    "index_metric_progress": {"zh": "处理中", "en": "In Progress"},
    "index_metric_closed": {"zh": "已关闭", "en": "Closed"},
    "index_recent_issues": {"zh": "### 📋 最近问题单", "en": "### 📋 Recent Issues"},
    "index_no_issues": {
        "zh": "暂无问题，点击左侧 ➕ 新建一个吧！",
        "en": "No issues yet. Click ➕ in the sidebar to create one!",
    },
    "index_quick_start": {"zh": "💡 快速上手", "en": "💡 Quick Start"},
    "index_btn_goto_dashboard": {"zh": "📊 前往数据大屏", "en": "📊 Go to Dashboard"},
    "index_quick_start_content": {
        "zh": "- **新建**: 点击左侧折叠区 `➕` 按钮开始创建。\n        - **搜索**: 使用侧边栏输入框进行关键字查询。\n        - **状态**: 点击流转按钮，文件会自动移动到相应目录下。\n        - **AI 友好**: 所有的内容都以 Markdown 存储在 `LocalStorage/issues` 下。",
        "en": "- **Create**: Click the `➕` button in the sidebar to start.\n        - **Search**: Use the sidebar input box to query by keyword.\n        - **Status**: Click a status button; the file moves automatically.\n        - **AI-Friendly**: All content is stored as Markdown in `LocalStorage/issues`.",
    },
    # --- Settings ---
    "settings_header": {"zh": "⚙️ 配置管理", "en": "⚙️ Settings"},
    "settings_users_header": {"zh": "👤 用户管理", "en": "👤 User Management"},
    "settings_add_user": {"zh": "➕ 添加新用户", "en": "➕ Add New User"},
    "settings_btn_add_user": {"zh": "➕ 添加用户", "en": "➕ Add User"},
    "settings_user_added": {"zh": "用户 {} 已添加！", "en": "User {} added!"},
    "settings_current_users": {"zh": "当前用户列表:", "en": "Current Users:"},
    "settings_projects_header": {"zh": "📁 项目管理", "en": "📁 Project Management"},
    "settings_add_project": {"zh": "➕ 添加新项目", "en": "➕ Add New Project"},
    "settings_btn_add_project": {"zh": "➕ 添加项目", "en": "➕ Add Project"},
    "settings_project_added": {"zh": "项目 {} 已添加！", "en": "Project {} added!"},
    "settings_current_projects": {"zh": "当前项目列表:", "en": "Current Projects:"},
    "settings_tags_header": {"zh": "🏷️ 标签管理", "en": "🏷️ Tag Management"},
    "settings_add_tag": {"zh": "➕ 添加新标签", "en": "➕ Add New Tag"},
    "settings_btn_add_tag": {"zh": "➕ 添加标签", "en": "➕ Add Tag"},
    "settings_tag_added": {"zh": "标签 {} 已添加！", "en": "Tag {} added!"},
    "settings_current_tags": {"zh": "当前标签列表:", "en": "Current Tags:"},
    # --- Attachment markdown templates ---
    "attach_link_md": {
        "zh": "📎 **附件**: [{}](../../attachments/{})",
        "en": "📎 **Attachment**: [{}](../../attachments/{})",
    },
    "attach_img_md": {
        "zh": "📷 **图片附件**:\n![{}](../../attachments/{})",
        "en": "📷 **Image Attachment**:\n![{}](../../attachments/{})",
    },
    "comment_header_md": {"zh": "---\n**💬 追评 [{}]**:\n{}", "en": "---\n**💬 Comment [{}]**:\n{}"},
    # --- Navigation & Breadcrumbs ---
    "nav_home": {"zh": "首页", "en": "Home"},
    "nav_main_views": {"zh": "主要视图", "en": "Main Views"},
    "nav_dashboard": {"zh": "数据看板", "en": "Dashboard"},
    "nav_all_issues": {"zh": "所有问题", "en": "All Issues"},
    "nav_quick_filters": {"zh": "快速视图", "en": "Quick Views"},
    "nav_system": {"zh": "系统", "en": "System"},
    "nav_settings": {"zh": "配置中心", "en": "Settings"},
    "nav_new_issue": {"zh": "➕ 新建问题单", "en": "➕ New Issue"},
    "nav_back": {"zh": "返回列表", "en": "Back to List"},
    # --- Status Native Translations ---
    "status_open": {"zh": "待处理", "en": "Open"},
    "status_in-progress": {"zh": "进行中", "en": "In Progress"},
    "status_fixed": {"zh": "已修复", "en": "Fixed"},
    "status_closed": {"zh": "已关闭", "en": "Closed"},
    # --- Data View & Toolbar ---
    "page_prev": {"zh": "上一页", "en": "Prev"},
    "page_next": {"zh": "下一页", "en": "Next"},
    "page_indicator": {"zh": "第 {} / {} 页", "en": "Page {} of {}"},
    # --- 🚀 新建问题单 button fix ---
    "create_btn_submit_short": {"zh": "🚀 创建问题", "en": "🚀 Create Issue"},
    # --- 🎨 Issue Header Enhancement ---
    "header_breadcrumb_home": {"zh": "首页", "en": "Home"},
    "header_breadcrumb_issues": {"zh": "问题列表", "en": "Issues"},
    "header_breadcrumb_detail": {"zh": "问题详情", "en": "Issue Detail"},
    "header_metadata_path": {"zh": "路径", "en": "Path"},
    "header_metadata_modified": {"zh": "最后修改", "en": "Last Modified"},
    "header_metadata_assignee": {"zh": "负责人", "en": "Assignee"},
    "header_metadata_tags": {"zh": "标签", "en": "Tags"},
    "header_actions_edit": {"zh": "编辑", "en": "Edit"},
    "header_actions_more": {"zh": "更多操作", "en": "More"},
    "header_actions_danger": {"zh": "危险操作", "en": "Danger"},
    "header_actions_delete": {"zh": "删除问题", "en": "Delete Issue"},
    "header_actions_copy": {"zh": "复制问题", "en": "Copy Issue"},
    "header_actions_export": {"zh": "导出链接", "en": "Export Link"},
    "header_status_current": {"zh": "当前状态", "en": "Current Status"},
    "header_status_transition": {"zh": "点击可切换", "en": "Click to change"},
    "header_confirm_delete": {"zh": "请再次确认删除操作", "en": "Please confirm delete operation"},
    "header_delete_success": {"zh": "问题已删除", "en": "Issue deleted"},
    "header_copy_success": {"zh": "问题已复制", "en": "Issue copied"},
    "header_copy_failed": {"zh": "复制失败", "en": "Copy failed"},
    "header_export_link": {"zh": "问题链接", "en": "Issue Link"},
    "header_export_copy": {"zh": "点击复制链接到剪贴板", "en": "Click to copy link to clipboard"},
}


def get_lang() -> str:
    """
    Return the active 2-letter language code.

    Priority:
    1. st.session_state._lang  (set by sidebar selector or previously detected)
    2. Browser navigator.language  (via streamlit-javascript, async on first render)
    3. 'en' as the universal default
    """
    try:
        import streamlit as st

        # Already set by user or a previous detection pass
        lang = getattr(st.session_state, "_lang", None)
        if lang:
            return lang

        # Try to read the browser locale once on first render
        try:
            from streamlit_javascript import st_javascript  # type: ignore[import]

            raw: str = st_javascript("navigator.language || navigator.userLanguage || 'en'")
            if raw and isinstance(raw, str):
                detected = raw.split("-")[0].lower()  # "zh-CN" → "zh"
                lang = detected if detected in ("zh", "en") else "en"
                st.session_state._lang = lang
                return lang
        except Exception:
            pass  # package not installed or JS not yet evaluated

        # First render: st_javascript returns 0 on the first pass (async)
        # We return 'en' and let the next render resolve it.
        st.session_state._lang = "en"
        return "en"
    except Exception:
        return "en"


def t(key: str, lang: str | None = None, *args: object) -> str:
    """
    Translate a string key to the active language.

    Args:
        key:  One of the keys in _STRINGS.
        lang: Override language code (optional).
        *args: Positional format arguments for .format() substitution.

    Returns:
        Translated string, falling back to zh if key/lang is missing.
    """
    if lang is None:
        lang = get_lang()
    entry = _STRINGS.get(key, {})
    result = entry.get(lang) or entry.get("zh") or key
    if args:
        result = result.format(*args)
    return result
