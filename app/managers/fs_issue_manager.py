import os
import json
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FileModifiedExternallyError(Exception):
    """当文件在外部被修改，导致乐观锁时间戳校验失败时抛出"""
    pass

class IssueNotFoundError(Exception):
    pass

class FileSystemIssueManager:
    """
    纯本地文件系统级别的问题单管理器 (Directory-as-a-Database)
    数据规范: {base_dir}/issues/{status}/{type}_{timestamp}_{title}.md
    """

    # 预定义的合法状态文件夹
    VALID_STATUSES = ["open", "in-progress", "fixed", "closed"]

    def __init__(self, base_dir: str = None):
        """
        初始化管理器
        Args:
            base_dir: 数据存储的根目录 (如果不传，默认使用环境变量 MARKISSUE_DATA_DIR 或 LocalStorage)
        """
        if base_dir is None:
            self.base_dir = Path(os.environ.get("MARKISSUE_DATA_DIR", "LocalStorage"))
        else:
            self.base_dir = Path(base_dir)
            
        self.issues_dir = self.base_dir / "issues"
        self.metadata_file = self.issues_dir / "metadata.json"
        
        self._init_directory_structure()

    def _init_directory_structure(self):
        """确保基础状态目录和字典存在"""
        self.issues_dir.mkdir(parents=True, exist_ok=True)
        
        for status in self.VALID_STATUSES:
            (self.issues_dir / status).mkdir(exist_ok=True)
            
        if not self.metadata_file.exists():
            self._save_metadata({})

    def _load_metadata(self) -> Dict[str, Any]:
        """加载关系和元数据字典"""
        if not self.metadata_file.exists():
            return {}
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Failed to parse metadata.json, returning empty.")
            return {}

    def _save_metadata(self, data: Dict[str, Any]):
        """保存关系和元数据字典"""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_json_list(self, filename: str) -> List[str]:
        path = self.issues_dir / filename
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _save_json_list(self, filename: str, data: List[str]):
        path = self.issues_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_users(self) -> List[str]:
        return self._load_json_list("users.json")

    def add_user(self, username: str):
        users = self.get_users()
        if username and username not in users:
            users.append(username)
            self._save_json_list("users.json", users)

    def get_projects(self) -> List[str]:
        return self._load_json_list("projects.json")

    def add_project(self, project: str):
        projects = self.get_projects()
        if project and project not in projects:
            projects.append(project)
            self._save_json_list("projects.json", projects)

    def remove_user(self, username: str):
        users = self.get_users()
        if username in users:
            users.remove(username)
            self._save_json_list("users.json", users)

    def remove_project(self, project: str):
        projects = self.get_projects()
        if project in projects:
            projects.remove(project)
            self._save_json_list("projects.json", projects)

    # --- Tags Management ---
    def get_tags(self) -> List[str]:
        return self._load_json_list("tags.json")

    def add_tag(self, tag: str):
        tags = self.get_tags()
        if tag and tag not in tags:
            tags.append(tag)
            self._save_json_list("tags.json", tags)

    def remove_tag(self, tag: str):
        tags = self.get_tags()
        if tag in tags:
            tags.remove(tag)
            self._save_json_list("tags.json", tags)

    def _parse_filename(self, filename: str) -> Optional[Dict[str, str]]:
        """
        解析文件名，提取类型、时间戳、标题 (即 ID)
        期望格式: prefix_timestamp_title.md (如 bug_20250228120000_login_failed.md)
        """
        stem = Path(filename).stem
        # 简单宽松的解析法则：以第一个下划线区分类型，整体作为 ID
        parts = stem.split("_", 1)
        if len(parts) < 2:
            issue_type = "unknown"
        else:
            issue_type = parts[0]
            
        return {
            "id": stem,          # 整个无后缀文件名作为唯一 ID
            "type": issue_type.upper(),
            "filename": filename
        }

    def _sanitize_filename(self, text: str) -> str:
        """清理不允许的字符，确保可作为安全的文件名"""
        # 替换非字母数字字符为下划线
        clean_text = re.sub(r'[^\w\u4e00-\u9fa5]+', '_', text)
        return clean_text.strip('_')

    def scan_all_issues(self) -> List[Dict[str, Any]]:
        """
        遍历目录树，返回所有问题的结构化快照列表（不读取全文）
        """
        issues = []
        metadata = self._load_metadata()
        
        for status in self.VALID_STATUSES:
            status_dir = self.issues_dir / status
            if not status_dir.exists():
                continue
                
            for file_path in status_dir.glob("*.md"):
                parsed = self._parse_filename(file_path.name)
                issue_id = parsed["id"]
                file_stat = file_path.stat()
                
                # 合并基础解析和额外的 metadata
                issue_data = {
                    "id": issue_id,
                    "type": parsed["type"],
                    "status": status.upper(),
                    "title": issue_id,  # 默认使用ID作为标题名，UI可以自己再处理
                    "filepath": str(file_path),
                    "last_modified": file_stat.st_mtime,
                    "created_at": file_stat.st_ctime
                }
                
                # 合并附加字典中的属性 (如 assignee, priority)
                extra = metadata.get(issue_id, {})
                issue_data.update(extra)
                
                issues.append(issue_data)
                
        # 默认按照创建时间倒序排
        issues.sort(key=lambda x: x["created_at"], reverse=True)
        return issues

    def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """
        根据 ID 查找单个 issue 的详细信息和原文内容
        """
        issues = self.scan_all_issues()
        for issue in issues:
            if issue["id"] == issue_id:
                try:
                    with open(issue["filepath"], "r", encoding="utf-8") as f:
                        content = f.read()
                    issue["content"] = content
                    return issue
                except Exception as e:
                    logger.error(f"Failed to read file {issue['filepath']}: {e}")
                    raise
                    
        raise IssueNotFoundError(f"Issue {issue_id} not found in any status folder.")

    def create_issue(self, issue_type: str, title: str, content: str, extra_meta: Dict[str, str] = None) -> str:
        """
        创建新的 Issue，默认放入 open/ 目录
        Returns:
            生成的 issue_id
        """
        timestamp = datetime.now().strftime("%Y%md%H%M%S")
        safe_title = self._sanitize_filename(title)
        safe_type = self._sanitize_filename(issue_type).lower()
        
        issue_id = f"{safe_type}_{timestamp}_{safe_title}"
        filename = f"{issue_id}.md"
        filepath = self.issues_dir / "open" / filename
        
        # 写入物理文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        # 写入元数据字典
        if extra_meta:
            self.update_metadata(issue_id, extra_meta)
            
        return issue_id

    def save_issue_content(self, issue_id: str, new_content: str, frontend_mtime: float) -> float:
        """
        保存内容，自带**乐观锁防覆盖保护**
        Args:
            issue_id: 唯一标示
            new_content: 更新后的 markdown 内容
            frontend_mtime: 前端持有的该文件的最后修改时间 (Unix Timestamp)
        Returns:
            new_mtime (写入成功后的最新时间戳)
        Raises:
            FileModifiedExternallyError: 当硬盘上的时间戳新于前端提供的时间戳时
        """
        issue = self.get_issue(issue_id)
        filepath = Path(issue["filepath"])
        
        # 获取当前硬盘上的真实最后修改时间
        current_mtime = filepath.stat().st_mtime
        
        # 比对时间戳 (考虑到浮点数精度，允许 0.1 秒的极其微小误差)
        if current_mtime - frontend_mtime > 0.1:
            raise FileModifiedExternallyError(
                f"文件在外部被修改！前端时间={frontend_mtime}, 服务器最新时间={current_mtime}"
            )
            
        # 安全验证通过，写入新内容
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        return filepath.stat().st_mtime

    def change_status(self, issue_id: str, new_status: str) -> bool:
        """
        通过移动跨目录移动文件改变状态
        """
        new_status = new_status.lower()
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
            
        issue = self.get_issue(issue_id)
        current_status = issue["status"].lower()
        
        if current_status == new_status:
            return True # 没变化
            
        old_path = Path(issue["filepath"])
        new_path = self.issues_dir / new_status / old_path.name
        
        # 执行物理移动
        shutil.move(str(old_path), str(new_path))
        return True

    def update_metadata(self, issue_id: str, updates: Dict[str, Any]):
        """更新附加属性字典"""
        meta = self._load_metadata()
        if issue_id not in meta:
            meta[issue_id] = {}
        
        meta[issue_id].update(updates)
        self._save_metadata(meta)

    def delete_issue(self, issue_id: str) -> bool:
        """
        永久删除一个问题单文件及其附加属性
        """
        try:
            issue = self.get_issue(issue_id)
        except IssueNotFoundError:
            return False
            
        filepath = Path(issue["filepath"])
        if filepath.exists():
            filepath.unlink()
            
        # 清洗元数据
        meta = self._load_metadata()
        if issue_id in meta:
            del meta[issue_id]
            self._save_metadata(meta)
            
        return True
