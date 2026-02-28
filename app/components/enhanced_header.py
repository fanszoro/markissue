"""
app/components/enhanced_header.py – Enhanced issue header with better UX and i18n support.

This module provides a redesigned issue header with:
- Beautiful breadcrumb navigation
- Clean metadata display
- Elegant status flow visualization
- Improved action buttons
- Full internationalization support
"""

import time
from datetime import datetime

import streamlit as st

from app.i18n import get_lang, t


def inject_custom_css():
    """Inject custom CSS for enhanced header styling."""
    st.markdown(
        """
    <style>
    /* 面包屑导航 */
    .breadcrumb-container {
        display: flex;
        align-items: center;
        font-size: 14px;
        margin-bottom: 16px;
        padding: 8px 12px;
        background: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #e9ecef;
    }

    .breadcrumb-current {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #495057;
        font-weight: 500;
        font-size: 14px;
        padding: 8px 12px;
        background: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #e9ecef;
    }

    .breadcrumb-item {
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .breadcrumb-link {
        color: #007bff;
        text-decoration: none;
        transition: color 0.2s ease;
    }

    .breadcrumb-link:hover {
        color: #0056b3;
        text-decoration: underline;
    }

    .breadcrumb-separator {
        margin: 0 8px;
        color: #6c757d;
        font-weight: bold;
    }

    .breadcrumb-item.active {
        color: #495057;
        font-weight: 500;
    }

    /* 主标题区域 */
    .title-section {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }

    .issue-type-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 6px 10px;
        border-radius: 4px;
        color: white;
        font-size: 12px;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        flex-shrink: 0;
    }

    .issue-type-badge.bug { background-color: #dc3545; }
    .issue-type-badge.fea { background-color: #007bff; }
    .issue-type-badge.opt { background-color: #ffc107; color: #212529; }
    .issue-type-badge.doc { background-color: #28a745; }
    .issue-type-badge.task { background-color: #6f42c1; }
    .issue-type-badge.default { background-color: #6c757d; }

    .issue-title {
        font-size: 24px;
        font-weight: 600;
        margin: 0;
        color: #212529;
        line-height: 1.3;
        flex: 1;
    }

    /* 元数据容器 */
    .metadata-container {
        margin: 16px 0;
        padding: 16px;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }

    .metadata-row {
        margin-bottom: 12px;
        display: flex;
        align-items: center;
    }

    .metadata-row:last-child {
        margin-bottom: 0;
    }

    .metadata-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        line-height: 1.4;
        width: 100%;
    }

    .metadata-label {
        font-weight: 500;
        color: #6c757d;
        min-width: 80px;
        flex-shrink: 0;
    }

    .metadata-value {
        color: #212529;
        font-weight: 400;
        flex: 1;
    }

    /* 状态流转 */
    .status-description {
        margin-bottom: 16px;
        padding: 12px 16px;
        background: #e3f2fd;
        border-radius: 6px;
        border-left: 4px solid #2196f3;
        font-size: 14px;
        color: #1565c0;
        line-height: 1.4;
    }

    .status-flow-container {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 20px 0;
        padding: 20px;
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .status-button {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 10px 16px;
        border: 2px solid;
        border-radius: 6px;
        background: transparent;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 14px;
        white-space: nowrap;
    }

    .status-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .status-button.current {
        color: white;
        font-weight: 600;
    }

    .status-arrow {
        font-size: 16px;
        color: #6c757d;
        margin: 0 4px;
    }

    /* 操作按钮组 */
    .action-buttons-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .danger-button {
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
        color: white !important;
    }

    .danger-button:hover {
        background-color: #c82333 !important;
        border-color: #c82333 !important;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .metadata-container {
            padding: 12px;
        }

        .metadata-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
            margin-bottom: 8px;
        }

        .metadata-item {
            width: 100%;
        }

        .metadata-label {
            min-width: auto;
        }

        .status-description {
            font-size: 13px;
            padding: 10px 12px;
        }

        .issue-title {
            font-size: 20px;
        }

        .breadcrumb-current {
            font-size: 13px;
        }

        .title-section {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }

        .issue-type-badge {
            align-self: flex-start;
        }
    }

    /* 深色模式支持 */
    @media (prefers-color-scheme: dark) {
        .breadcrumb-current,
        .metadata-container {
            background: #2d3748;
            border-color: #4a5568;
            color: #e2e8f0;
        }

        .issue-title {
            color: #e2e8f0;
        }

        .status-flow-container {
            background: #2d3748;
            border-color: #4a5568;
        }

        .status-description {
            background: #1a365d;
            color: #90cdf4;
            border-color: #2b6cb0;
        }

        .metadata-label {
            color: #a0aec0;
        }

        .metadata-value {
            color: #e2e8f0;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def get_issue_type_config(issue_type: str) -> dict:
    """Get issue type configuration including icon and color."""
    type_configs = {
        "bug": {"icon": "🐞", "color": "#e53e3e", "label": "BUG"},  # Red-ish
        "fea": {"icon": "✨", "color": "#3182ce", "label": "FEA"},  # Blue
        "opt": {"icon": "⚡", "color": "#d69e2e", "label": "OPT"},  # Gold
        "doc": {"icon": "📖", "color": "#38a169", "label": "DOC"},  # Green
        "task": {"icon": "📋", "color": "#805ad5", "label": "TASK"},  # Purple
    }
    return type_configs.get(issue_type.lower(), {"icon": "📄", "color": "#718096", "label": issue_type.upper()})


def get_status_config(status: str) -> dict:
    """Get status configuration including icon and color."""
    status_configs = {
        "open": {"icon": "⚪", "color": "#718096", "label": t("status_open")},  # Gray/Open
        "in-progress": {"icon": "🔵", "color": "#3182ce", "label": t("status_in-progress")},  # Blue/Progress
        "fixed": {"icon": "🟢", "color": "#38a169", "label": t("status_fixed")},  # Green/Fixed
        "closed": {"icon": "✅", "color": "#2d3748", "label": t("status_closed")},  # Dark/Closed
    }
    return status_configs.get(status.lower(), {"icon": "❓", "color": "#718096", "label": status})


def format_timestamp(ts: int) -> str:
    """Format timestamp for display."""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def render_breadcrumb_navigation(issue: dict):
    """
    Render beautiful breadcrumb navigation with functional links and precise spacing.
    Uses proportional weights to ensure a tight, natural 'text-like' feel.
    """
    home_label = t("header_breadcrumb_home")
    issues_label = t("header_breadcrumb_issues")

    # Calculate weights based on text length + icon (roughly)
    w_home = len(home_label) + 4
    w_issues = len(issues_label) + 4
    w_sep = 1
    w_current = 20

    # Create columns with aggressive trailing weight to squeeze links to the left
    cols = st.columns([w_home, w_sep, w_issues, w_sep, w_current, 50], gap="small")

    with cols[0]:
        if st.button(f"🏠 {home_label}", key="bc_home", type="tertiary", use_container_width=True):
            st.session_state.current_view = "index"
            st.rerun()

    with cols[1]:
        st.markdown(
            '<div style="color: #cbd5e0; line-height: 2.2; text-align: center; width: 100%;">›</div>',
            unsafe_allow_html=True,
        )

    with cols[2]:
        if st.button(f"📋 {issues_label}", key="bc_issues", type="tertiary", use_container_width=True):
            st.session_state.current_view = "all_issues"
            st.rerun()

    with cols[3]:
        st.markdown(
            '<div style="color: #cbd5e0; line-height: 2.2; text-align: center; width: 100%;">›</div>',
            unsafe_allow_html=True,
        )

    with cols[4]:
        title_truncated = issue["title"][:50] + ("..." if len(issue["title"]) > 50 else "")
        st.markdown(
            f'<div style="color: #718096; font-size: 0.9em; line-height: 2.5; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">📄 {title_truncated}</div>',
            unsafe_allow_html=True,
        )


def render_issue_title_section(issue: dict):
    """Render enhanced issue title with type badge."""
    type_config = get_issue_type_config(issue["type"])

    # Single row layout for type badge and title
    st.markdown(
        f"""
    <div class="title-section">
        <div class="issue-type-badge {issue['type']}">
            <span class="badge-icon">{type_config['icon']}</span>
            <span class="badge-text">{type_config['label']}</span>
        </div>
        <h1 class="issue-title">
            {issue['title']}
        </h1>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_issue_metadata(issue: dict):
    """Render clean metadata display with improved spacing."""
    tags_html = ""
    if issue.get("tags"):
        tags_html = " | ".join([f"🏷️ `{tag}`" for tag in issue["tags"]])

    st.markdown(
        f"""
    <div class="metadata-container">
        <div class="metadata-row">
            <div class="metadata-item">
                📁 <span class="metadata-label">{t('header_metadata_path')}:</span>
                <span class="metadata-value">`{issue['filepath']}`</span>
            </div>
        </div>
        <div class="metadata-row">
            <div class="metadata-item">
                🕒 <span class="metadata-label">{t('header_metadata_modified')}:</span>
                <span class="metadata-value">{format_timestamp(issue['last_modified'])}</span>
            </div>
        </div>
        <div class="metadata-row">
            <div class="metadata-item">
                👤 <span class="metadata-label">{t('header_metadata_assignee')}:</span>
                <span class="metadata-value">{issue.get('assignee', '未指派' if get_lang() == 'zh' else 'Unassigned')}</span>
            </div>
        </div>
        <div class="metadata-row">
            <div class="metadata-item">
                🏷️ <span class="metadata-label">{t('header_metadata_tags')}:</span>
                <span class="metadata-value">{tags_html or ('无' if get_lang() == 'zh' else 'None')}</span>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_status_flow_section(issue: dict, manager):
    """Render elegant status flow visualization with functional buttons."""
    current_status = issue["status"].lower()

    # Define status order
    status_order = ["open", "in-progress", "fixed", "closed"]

    # Initialize session state key if not exists
    if "status_change" not in st.session_state:
        st.session_state.status_change = None

    # Status description with proper styling
    current_status_label = get_status_config(current_status)["label"]
    st.markdown(
        f"""
    <div class="status-description">
        📊 {t('header_status_current')}: <strong>{current_status_label}</strong> | {t('header_status_transition')}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Create status flow buttons with better spacing
    cols = st.columns([2, 1, 2, 1, 2, 1, 2])

    for i, status_key in enumerate(status_order):
        config = get_status_config(status_key)
        is_current = status_key == current_status
        col_idx = i * 2

        with cols[col_idx]:
            button_type = "primary" if is_current else "secondary"
            button_label = f"{config['icon']} {config['label']}"

            if is_current:
                st.button(
                    button_label,
                    key=f"status_{status_key}_current",
                    use_container_width=True,
                    type=button_type,
                    disabled=True,
                )
            else:
                if st.button(button_label, key=f"status_{status_key}", use_container_width=True, type=button_type):
                    try:
                        if manager.change_status(issue["id"], status_key):
                            st.success(t("issue_moved").format(config["label"]))
                            time.sleep(0.5)
                            st.rerun()
                    except Exception as e:
                        st.error(f"状态变更失败: {e}")

        if i < len(status_order) - 1:
            with cols[col_idx + 1]:
                st.markdown(
                    '<div style="text-align: center; font-size: 1.2rem; color: #6c757d; padding: 8px 0;">→</div>',
                    unsafe_allow_html=True,
                )


def render_action_buttons(issue: dict, manager):
    """Render enhanced action buttons with better layout and functionality."""

    # Edit and More buttons side by side
    col_edit, col_more = st.columns([1, 1])

    with col_edit:
        if st.button(
            f"🛠️ {t('header_actions_edit')}", use_container_width=True, key="enhanced_edit_issue", type="secondary"
        ):
            st.session_state.edit_mode = True
            st.rerun()

    with col_more:
        with st.popover(f"⚙️ {t('header_actions_more')}"):
            # Copy issue
            if st.button(f"📋 {t('header_actions_copy')}", use_container_width=True, key="enhanced_copy_issue"):
                try:
                    # Create a copy of the issue with correct parameters
                    copy_title = f"{issue['title']} (副本)"
                    copy_content = issue["content"]
                    copy_type = issue["type"]
                    copy_extra = {
                        "assignee": issue.get("assignee", ""),
                        "project": issue.get("project", ""),
                        "priority": issue.get("priority", "Medium"),
                        "tags": issue.get("tags", []),
                    }

                    new_id = manager.create_issue(copy_type, copy_title, copy_content, copy_extra)
                    st.success(t("header_copy_success"))
                    time.sleep(1)
                    st.session_state.selected_issue_id = new_id
                    st.rerun()
                except Exception as e:
                    st.error(f"{t('header_copy_failed')}: {e}")

            # Export link
            if st.button(f"🔗 {t('header_actions_export')}", use_container_width=True, key="enhanced_export_link"):
                issue_id = issue["id"]
                copied_text = "链接已成功复制!" if get_lang() == "zh" else "Link copied!"

                # Render everything in one block to ensure JS target exists
                st.markdown(
                    f"""
                <div style="padding: 12px; background: #f8fafc; border-radius: 8px; margin: 10px 0; border: 1px solid #e2e8f0;">
                    <div style="font-size: 12px; color: #64748b; margin-bottom: 6px; font-weight: 500;">🔗 {t('header_export_link')}</div>
                    <code id="export-url" style="word-break: break-all; color: #0f172a; font-size: 13px; background: white; padding: 4px 8px; display: block; border-radius: 4px; border: 1px solid #e2e8f0; margin-bottom: 8px;">{issue_id}</code>
                    <div style="font-size: 11px; color: #94a3b8;">{t('header_export_copy')}</div>
                </div>

                <script>
                (function() {{
                    // Wait a moment for Streamlit's iframe/DOM to stabilize
                    setTimeout(() => {{
                        let urlStr = "id: " + "{issue_id}";
                        try {{
                            // Use window.parent if in iframe, but be careful of cross-origin
                            const fullUrl = window.location.href.split('?')[0].split('#')[0];
                            urlStr = fullUrl + '?issue={issue_id}';
                        }} catch(e) {{
                            console.log("Could not get full URL, using fallback");
                        }}

                        const el = document.getElementById('export-url');
                        if (el) el.textContent = urlStr;

                        // Copy functionality
                        try {{
                            const tempInput = document.createElement('textarea');
                            tempInput.style.position = 'fixed';
                            tempInput.style.left = '-9999px';
                            tempInput.value = urlStr;
                            document.body.appendChild(tempInput);
                            tempInput.select();
                            document.execCommand('copy');
                            document.body.removeChild(tempInput);

                            // Visual feedback
                            const toast = document.createElement('div');
                            toast.textContent = "{copied_text}";
                            toast.style.cssText = "position:fixed;top:20px;right:20px;padding:12px 24px;background:#1e293b;color:white;border-radius:8px;z-index:999999;font-size:14px;box-shadow:0 10px 15px -3px rgba(0,0,0,0.1);font-family:sans-serif;pointer-events:none;";
                            document.body.appendChild(toast);
                            setTimeout(() => {{
                                toast.style.transition = "opacity 0.5s";
                                toast.style.opacity = "0";
                                setTimeout(() => {{ document.body.removeChild(toast); }}, 500);
                            }}, 1500);
                        }} catch (err) {{
                            console.error('Copy failed', err);
                        }}
                    }}, 150);
                }})();
                </script>
                """,
                    unsafe_allow_html=True,
                )

            st.divider()

            # Danger operations
            st.markdown("**⚠️ 危险操作**")
            if st.button(
                f"🗑️ {t('header_actions_delete')}", use_container_width=True, key="enhanced_delete_issue", type="primary"
            ):
                if st.session_state.get(f"confirm_delete_{issue['id']}", False):
                    try:
                        manager.delete_issue(issue["id"])
                        st.success(t("header_delete_success"))
                        st.session_state.selected_issue_id = None
                        time.sleep(0.8)
                        st.rerun()
                    except Exception as e:
                        st.error(f"删除失败: {e}")
                else:
                    st.session_state[f"confirm_delete_{issue['id']}"] = True
                    st.warning(t("header_confirm_delete"))


def render_enhanced_issue_header(issue: dict, manager):
    """Main function to render the complete enhanced issue header."""

    # Inject custom CSS
    inject_custom_css()

    # Main layout
    col_left, col_right = st.columns([3, 1])

    with col_left:
        # Breadcrumb navigation
        render_breadcrumb_navigation(issue)

        # Title section
        render_issue_title_section(issue)

        # Metadata
        render_issue_metadata(issue)

    with col_right:
        # Action buttons
        render_action_buttons(issue, manager)

    # Status flow section (full width)
    render_status_flow_section(issue, manager)

    # Divider
    st.divider()


# Utility functions for backward compatibility
def get_status_order(status: str) -> int:
    """Get numeric order for status comparison."""
    orders = {"open": 0, "in-progress": 1, "fixed": 2, "closed": 3}
    return orders.get(status.lower(), 99)
