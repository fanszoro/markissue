import streamlit as st


def inject_markdown_css():
    """Injects professional documentation-style CSS for markdown content."""
    st.markdown(
        """
    <style>
    /* Content Area Container */
    .markdown-content-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
        line-height: 1.6;
        color: #1e293b;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px 0;
    }

    /* Typography */
    .markdown-content-container h1,
    .markdown-content-container h2,
    .markdown-content-container h3 {
        color: #0f172a;
        font-weight: 700;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        letter-spacing: -0.02em;
    }

    .markdown-content-container h1 { font-size: 2.25rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3em; }
    .markdown-content-container h2 { font-size: 1.8rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3em; }
    .markdown-content-container h3 { font-size: 1.5rem; }

    .markdown-content-container p {
        margin-bottom: 1.25em;
    }

    /* Lists */
    .markdown-content-container ul,
    .markdown-content-container ol {
        margin-bottom: 1.25em;
        padding-left: 2em;
    }

    .markdown-content-container li {
        margin-bottom: 0.5em;
    }

    /* Blockquotes */
    .markdown-content-container blockquote {
        border-left: 4px solid #3b82f6;
        background: #f8fafc;
        padding: 1rem 1.5rem;
        margin: 1.5rem 0;
        color: #475569;
        font-style: italic;
        border-radius: 0 8px 8px 0;
    }

    /* Code Blocks */
    .markdown-content-container code {
        background: #f1f5f9;
        padding: 0.2em 0.4em;
        border-radius: 4px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.9em;
        color: #ef4444;
    }

    .markdown-content-container pre {
        background: #1e293b !important;
        padding: 1.25rem !important;
        border-radius: 12px !important;
        margin: 1.5rem 0 !important;
        overflow-x: auto !important;
        border: 1px solid #334155 !important;
    }

    .markdown-content-container pre code {
        background: transparent !important;
        color: #e2e8f0 !important;
        padding: 0 !important;
    }

    /* Tables */
    .markdown-content-container table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
        font-size: 0.95em;
    }

    .markdown-content-container th {
        background: #f8fafc;
        text-align: left;
        padding: 0.75rem 1rem;
        border: 1px solid #e2e8f0;
        font-weight: 600;
    }

    .markdown-content-container td {
        padding: 0.75rem 1rem;
        border: 1px solid #e2e8f0;
    }

    /* Images */
    .markdown-content-container img {
        max-width: 100%;
        height: auto;
        border-radius: 12px;
        margin: 2rem auto;
        display: block;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Dark Mode Adjustments */
    @media (prefers-color-scheme: dark) {
        .markdown-content-container {
            color: #cbd5e0;
        }
        .markdown-content-container h1,
        .markdown-content-container h2,
        .markdown-content-container h3 {
            color: #f8fafc;
        }
        .markdown-content-container h1,
        .markdown-content-container h2 {
            border-bottom-color: #334155;
        }
        .markdown-content-container blockquote {
            background: #1e293b;
            color: #94a3b8;
        }
        .markdown-content-container code {
            background: #334155;
            color: #f87171;
        }
        .markdown-content-container th {
            background: #0f172a;
            border-color: #334155;
        }
        .markdown-content-container td {
            border-color: #334155;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_markdown(content):
    """Renders markdown content within the styled container."""
    inject_markdown_css()
    st.markdown('<div class="markdown-content-container">', unsafe_allow_html=True)
    st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)
