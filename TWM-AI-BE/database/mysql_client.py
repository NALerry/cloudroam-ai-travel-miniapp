# database/mysql_client.py
import pymysql
import json
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from config import Config


class MySQLClient:
    def __init__(self):
        self.config = {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': True  # 关键：开启自动提交
        }
        # 确保数据库存在
        self._ensure_database()

    def _ensure_database(self):
        """确保数据库存在"""
        try:
            config = self.config.copy()
            config.pop('database')
            config.pop('cursorclass')
            config.pop('autocommit', None)
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {self.config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            conn.close()
        except Exception as e:
            print(f"创建数据库失败: {e}")

    @contextmanager
    def get_connection(self):
        conn = pymysql.connect(**self.config)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # ========== 会话管理 ==========
    def create_session(self, user_id: str, session_id: str = None, title: str = "新对话") -> str:
        import uuid
        if not session_id:
            session_id = str(uuid.uuid4())

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 检查是否已存在
            cursor.execute("SELECT session_id FROM chat_sessions WHERE session_id = %s", (session_id,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO chat_sessions (session_id, user_id, title) VALUES (%s, %s, %s)",
                    (session_id, user_id, title)
                )
                # 初始化结构化上下文
                cursor.execute(
                    "INSERT INTO session_context (session_id, user_id) VALUES (%s, %s)",
                    (session_id, user_id)
                )
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chat_sessions WHERE session_id = %s",
                (session_id,)
            )
            return cursor.fetchone()

    def get_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id, title, created_at, updated_at FROM chat_sessions "
                "WHERE user_id = %s ORDER BY updated_at DESC LIMIT %s",
                (user_id, limit)
            )
            return cursor.fetchall()

    # ========== 消息管理 ==========
    def save_message(self, session_id: str, user_id: str, role: str, content: str):
        """保存消息 - 修复外键问题"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 第一步：确保会话存在
            cursor.execute("SELECT session_id FROM chat_sessions WHERE session_id = %s", (session_id,))
            if not cursor.fetchone():
                # 会话不存在，创建新会话
                print(f"📝 会话不存在，自动创建: {session_id}")
                cursor.execute(
                    "INSERT INTO chat_sessions (session_id, user_id, title) VALUES (%s, %s, %s)",
                    (session_id, user_id, "新对话")
                )
                # 创建会话上下文
                cursor.execute(
                    "INSERT INTO session_context (session_id, user_id) VALUES (%s, %s)",
                    (session_id, user_id)
                )
                # 立即提交，确保会话记录持久化
                conn.commit()

            # 第二步：保存消息
            cursor.execute(
                "INSERT INTO chat_messages (session_id, user_id, role, content) VALUES (%s, %s, %s, %s)",
                (session_id, user_id, role, content)
            )
            return cursor.lastrowid

    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, created_at FROM chat_messages "
                "WHERE session_id = %s ORDER BY created_at DESC LIMIT %s",
                (session_id, limit)
            )
            messages = cursor.fetchall()
            for msg in messages:
                if msg.get('content') is None:
                    msg['content'] = ''
            return list(reversed(messages))

    # ========== 结构化上下文管理 ==========
    def get_session_context(self, session_id: str) -> Dict:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM session_context WHERE session_id = %s",
                (session_id,)
            )
            result = cursor.fetchone()

            if result is None:
                return {}

            # 解析JSON字段
            try:
                if result.get('order_info') and isinstance(result['order_info'], str):
                    result['order_info'] = json.loads(result['order_info'])
                if result.get('task_state') and isinstance(result['task_state'], str):
                    result['task_state'] = json.loads(result['task_state'])
                if result.get('pending_info') and isinstance(result['pending_info'], str):
                    result['pending_info'] = json.loads(result['pending_info'])
                if result.get('extra_data') and isinstance(result['extra_data'], str):
                    result['extra_data'] = json.loads(result['extra_data'])
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")

            return result

    def update_session_context(self, session_id: str, updates: Dict):
        """更新结构化上下文"""
        for field in ['order_info', 'task_state', 'pending_info', 'extra_data']:
            if field in updates and updates[field] is not None:
                if isinstance(updates[field], (dict, list)):
                    updates[field] = json.dumps(updates[field], ensure_ascii=False)

        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [session_id]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE session_context SET {set_clause}, updated_at = NOW() WHERE session_id = %s",
                values
            )

    # ========== 反馈管理 ==========
    def save_feedback(self, session_id: str, user_id: str, rating: int, feedback_text: str = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO feedback_records (session_id, user_id, rating, feedback_text) VALUES (%s, %s, %s, %s)",
                (session_id, user_id, rating, feedback_text)
            )