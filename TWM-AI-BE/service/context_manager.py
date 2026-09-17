# service/context_manager.py
import json
import traceback
from typing import Dict, List
from database.mysql_client import MySQLClient
from config import Config


class ContextManager:
    """
    结构化上下文管理器
    解决上下文窗口溢出问题：将用户信息、订单信息、任务状态单独存储
    """

    def __init__(self):
        self.mysql = MySQLClient()

    def build_structured_context(self, session_id: str) -> str:
        """构建结构化上下文，用于发送给LLM"""
        try:
            print(f"build_structured_context: session_id={session_id}")
            context = self.mysql.get_session_context(session_id)
            print(f"获取到的context类型: {type(context)}")

            # 如果 context 是 None 或空，返回空字符串
            if not context:
                print("context 为空，返回空字符串")
                return ""

            if not isinstance(context, dict):
                print(f"context 不是字典类型: {type(context)}")
                return ""

            context_parts = []

            # 用户信息
            user_info = []
            if context.get('user_name'):
                user_info.append(f"用户姓名：{context['user_name']}")
            if context.get('user_phone'):
                user_info.append(f"联系电话：{context['user_phone']}")
            if context.get('user_level'):
                user_info.append(f"会员等级：{context['user_level']}")

            if user_info:
                context_parts.append("【用户信息】\n" + "\n".join(user_info))

            # 订单信息
            if context.get('current_order_id'):
                order_info = f"当前订单号：{context['current_order_id']}"
                if context.get('order_info'):
                    order_info += f"\n订单详情：{context['order_info']}"
                context_parts.append("【订单信息】\n" + order_info)

            # 任务状态
            if context.get('current_intent'):
                task_info = f"当前任务：{context['current_intent']}"
                if context.get('task_state'):
                    task_info += f"\n任务进度：{context['task_state']}"
                context_parts.append("【任务状态】\n" + task_info)

            # 待补充信息
            if context.get('pending_info'):
                pending = context['pending_info']
                if isinstance(pending, dict):
                    pending_text = "需要收集的信息：\n"
                    for field, status in pending.items():
                        if isinstance(status, dict) and not status.get('collected'):
                            pending_text += f"- 需要{status.get('description', field)}\n"
                    if pending_text != "需要收集的信息：\n":
                        context_parts.append(pending_text)

            result = "\n\n".join(context_parts)
            return result

        except Exception as e:
            print(f"build_structured_context 异常: {e}")
            print(traceback.format_exc())
            return ""

    def extract_and_update_intent(self, session_id: str, user_message: str, intent: str):
        """提取并更新用户意图"""
        try:
            context = self.mysql.get_session_context(session_id)
            if not context:
                return

            current_intent = context.get('current_intent')

            # 如果意图发生变化，重置任务状态
            if current_intent != intent:
                self.mysql.update_session_context(session_id, {
                    'current_intent': intent,
                    'task_state': json.dumps({'step': 0, 'status': 'in_progress'}),
                    'pending_info': json.dumps({})
                })
        except Exception as e:
            print(f"extract_and_update_intent 异常: {e}")

    def update_pending_info(self, session_id: str, field: str, description: str):
        """记录需要收集的信息"""
        try:
            context = self.mysql.get_session_context(session_id)
            if not context:
                return

            pending = context.get('pending_info', {})
            if not isinstance(pending, dict):
                pending = {}

            pending[field] = {
                'collected': False,
                'description': description,
                'value': None
            }

            self.mysql.update_session_context(session_id, {
                'pending_info': json.dumps(pending, ensure_ascii=False)
            })
        except Exception as e:
            print(f"update_pending_info 异常: {e}")

    def mark_info_collected(self, session_id: str, field: str, value: str):
        """标记信息已收集"""
        try:
            context = self.mysql.get_session_context(session_id)
            if not context:
                return False

            pending = context.get('pending_info', {})
            if not isinstance(pending, dict):
                return False

            if field in pending:
                pending[field]['collected'] = True
                pending[field]['value'] = value

                self.mysql.update_session_context(session_id, {
                    'pending_info': json.dumps(pending, ensure_ascii=False)
                })
                return True
            return False
        except Exception as e:
            print(f"mark_info_collected 异常: {e}")
            return False

    def is_waiting_for_info(self, session_id: str) -> Dict:
        """检查是否在等待用户补充信息"""
        try:
            context = self.mysql.get_session_context(session_id)
            if not context or not isinstance(context, dict):
                return {'is_waiting': False, 'fields': []}

            pending = context.get('pending_info', {})
            if not isinstance(pending, dict):
                return {'is_waiting': False, 'fields': []}

            waiting_for = []
            for field, info in pending.items():
                if isinstance(info, dict) and not info.get('collected'):
                    waiting_for.append({
                        'field': field,
                        'description': info.get('description', field)
                    })

            return {
                'is_waiting': len(waiting_for) > 0,
                'fields': waiting_for
            }
        except Exception as e:
            print(f"is_waiting_for_info 异常: {e}")
            return {'is_waiting': False, 'fields': []}