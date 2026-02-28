# 📁 MarkIssue
![Python](https://img.shields.io/badge/Python-3.12-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B) ![NoDB](https://img.shields.io/badge/Database-None-success)

**MarkIssue** 是一款极其轻巧、所见即所得的敏捷问题追踪系统 (Issue Tracker)。
它让你彻底告别厚重的数据库和繁琐的后台配置，以最极简、最直观的方式管理你的项目进度。

[🚀 立即体验在线 Demo](https://bf3tzdtgrlfvvhjche5nuf.streamlit.app/)


## 💡 为什么选择 MarkIssue？ (Why MarkIssue?)

- **极度适合个人与小型团队**：没有重型数据库，无需配置权限系统，克隆即用。
- **极佳的大规模生成文档管理平台**：不仅适用于修复 Bug 的流转，还能完美承载大量利用 AI 批量生成或散落的 Markdown 文档，供你系统性地阅读、打标、分类与整理归档。
- **专为 "Vibe Coding" (AI 辅助编程) 打造**：
  - 数据全部以最原始、高清晰度的 `.md` (Markdown) 和 `.json` 落地存储。
  - 你随时可以把整个项目目录打包扔给大模型（Cursor/Copilot/GPT），AI 能够以 `100%` 的精度帮你分析这周解决了什么 Bug、还有多少没修、并一键生成精美的总结报告！
  - 它不是要把人锁在系统里，而是**让所有的工作上下文都完美暴露且兼容现代 AI 编程流**。

## 🌟 核心特性
除了基础的增删查改与状态流转，MarkIssue 提供了一系列极具生产力的功能：

- **🏷️ 多标签分类系统**：支持为问题单挂载自定义标签组（如 `frontend`, `urgent` 等），方便快速过滤寻找目标。
- **📊 全景数据看板**：内置自动生成的图表与数据，随时掌控各状态进度、问题类型分布，以及谁身上的积压工作最多。
- **💬 快速追评机制**：在浏览问题时，无需进入编辑模式，可直接在页面最下方“一键追评”，随时记录最新进度的讨论留痕。
- **📎 拖拽式图文附件**：直接将截图拖入系统，即可自动生成相应的 Markdown 引用的图文排版并追加到了正文中，告别繁琐的找图传图。
- **⚙️ 全面的后台字典管理**：直接在 Web 端管理你的项目字典（Projects）、成员字典（Assignees）和标签字典（Tags）。

---

## 📸 界面预览

### 1. 全景数据看板
![Dashboard](docs/images/dashboard.png)

### 2. 问题工作台与附件交互
![Issue View](docs/images/issue_view.png)

### 3. 配置管理中心
![Settings View](docs/images/settings_view.png)

---

## 🚀 部署与运行指南

MarkIssue 提供了三种极速拉起的方式，开箱即用。应用程序默认启动在 `8505` 端口。

### 方式一：裸机直接运行 (本地开发/体验推荐)
仅需克隆仓库并安装 Python 依赖：
```bash
# 1. 克隆并进入目录
git clone https://github.com/fanszoro/markissue.git
cd markissue

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
streamlit run tracker_app.py --server.port 8505 --server.address 127.0.0.1
# 应用将在 http://localhost:8505 打开
```

### 方式二：Docker 本地容器化 (内网/私人服务器推荐)
使用 Docker 可以最大程度保持你的宿主机环境的纯净。
我们推荐使用内建的 `docker-compose.yml`：
```bash
# 一键后台启动容器
make docker-up

# 或直接使用原生的: docker-compose up -d
```
> **数据持久化说明**：容器里的生成数据会安全地映射保存在宿主机当前的 `./LocalStorage` 文件夹中。

### ⚙️ 环境与配置变量 (Environment Variables)
MarkIssue 遵循最少配置原则，系统本身只保留了一个最核心的数据目录变更入口，其余皆可使用 Streamlit 原生的启动参数调节：

| 变量名 / 参数 | 说明 | 默认值 | 示例用法 |
| --- | --- | --- | --- |
| `MARKISSUE_DATA_DIR` | 指定 Markdown 文件与系统的保存/读取目录。非常适合将数据文件与代码完全物理隔离。 | `LocalStorage` | `export MARKISSUE_DATA_DIR=/var/data/issues` <br> `make run` |
| `--server.port` | **Streamlit 原生参数**：指定 Web 服务的运行端口。 | `8505` | `streamlit run tracker_app.py --server.port 8080` |
| `--server.address` | **Streamlit 原生参数**：指定监听的地址，局域网建议设置为 `0.0.0.0`。 | `localhost` 或 `0.0.0.0` | `streamlit run tracker_app.py --server.address 0.0.0.0` |
