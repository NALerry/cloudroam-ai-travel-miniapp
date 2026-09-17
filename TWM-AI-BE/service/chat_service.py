# service/chat_service.py
import asyncio
import json
import traceback
import httpx
import datetime
import os
from typing import Dict, List, Optional
from database.mysql_client import MySQLClient
from service.rag_service import RAGService
from service.context_manager import ContextManager
from config import Config


class ChatService:
    def __init__(self):
        self.mysql = MySQLClient()
        self.rag = RAGService()
        self.context_manager = ContextManager()

        self.prompt_log_dir = "./prompt_logs"
        if not os.path.exists(self.prompt_log_dir):
            os.makedirs(self.prompt_log_dir)

    async def process_message(self, user_id: str, session_id: str, message: str) -> Dict:
        try:
            print(f"\n{'=' * 60}")
            print(f"🚀 开始处理消息")
            print(f"   用户ID: {user_id}")
            print(f"   会话ID: {session_id}")
            print(f"   消息: {message}")
            print(f"{'=' * 60}")

            # 确保会话存在
            existing_session = self.mysql.get_session(session_id)
            if not existing_session:
                print(f"📝 会话不存在，自动创建: {session_id}")
                self.mysql.create_session(user_id, session_id, "新对话")
                print(f"✅ 会话创建成功")
            else:
                print(f"✅ 会话已存在")

            self.mysql.save_message(session_id, user_id, 'user', message)
            print("✅ 保存用户消息成功")

            history = self.mysql.get_messages(session_id, Config.MAX_HISTORY_MESSAGES)
            print(f"✅ 获取历史消息成功，共 {len(history)} 条")

            structured_context = self.context_manager.build_structured_context(session_id)
            print(f"✅ 结构化上下文: {structured_context[:100] if structured_context else '空'}")

            waiting_info = self.context_manager.is_waiting_for_info(session_id)
            print(f"✅ 等待信息: {waiting_info}")

            intent = self._recognize_intent(message)
            print(f"✅ 意图识别: {intent}")

            self.context_manager.extract_and_update_intent(session_id, message, intent)
            print("✅ 意图更新成功")

            print(f"\n📚 开始检索知识库...")
            knowledge_context = await self.rag.retrieve_context(message)
            print(f"📚 知识库检索结果: has_knowledge={knowledge_context.get('has_knowledge', False)}")

            if knowledge_context.get('has_knowledge'):
                print(f"📚 知识库上下文长度: {len(knowledge_context.get('context', ''))} 字符")
                print(f"📚 知识来源数量: {len(knowledge_context.get('sources', []))}")
            else:
                print(f"⚠️ 知识库检索返回空结果！")

            prompt = self._build_prompt(
                user_message=message,
                history=history,
                structured_context=structured_context,
                knowledge=knowledge_context,
                waiting_info=waiting_info
            )
            print(f"✅ Prompt构建成功，长度: {len(prompt)} 字符")

            self._save_prompt_to_file(prompt, user_id, session_id, message)

            response = await self._call_llm(prompt, knowledge_context, message, session_id, user_id)
            print(f"✅ LLM回复生成成功，长度: {len(response)} 字符")

            self.mysql.save_message(session_id, user_id, 'assistant', response)
            print("✅ 保存AI回复成功")

            return {
                'success': True,
                'content': response,
                'sources': knowledge_context.get('sources', []) if knowledge_context.get('has_knowledge') else []
            }

        except Exception as e:
            print(f"❌ 处理消息失败: {e}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }

    def _save_prompt_to_file(self, prompt: str, user_id: str, session_id: str, message: str):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            safe_session_id = session_id[:8] if session_id else "nosession"
            safe_user_id = user_id[:8] if user_id else "nouser"
            filename = f"prompt_{timestamp}_{safe_user_id}_{safe_session_id}.txt"
            filepath = os.path.join(self.prompt_log_dir, filename)

            file_content = f"""
{'=' * 80}
PROMPT LOG - TWM 智能客服
{'=' * 80}

【基本信息】
- 时间戳: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}
- 用户ID: {user_id}
- 会话ID: {session_id}
- Prompt长度: {len(prompt)} 字符

【用户消息】
{message}

{'=' * 80}
【完整 Prompt 内容】
{'=' * 80}

{prompt}

{'=' * 80}
【Prompt 结束】
{'=' * 80}
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)

            print(f"✅ Prompt已保存到文件: {filepath}")

        except Exception as e:
            print(f"❌ 保存Prompt文件失败: {e}")

    def _recognize_intent(self, message: str) -> str:
        intents = {
            'query_order': ['订单', '查询', '物流', '快递', '在哪', '状态'],
            'cancel_order': ['取消', '退货', '退款', '不要了'],
            'complaint': ['投诉', '不满', '差评', '生气', '失望'],
            'consultation': ['咨询', '请问', '怎么', '如何', '什么'],
            'faq': ['规则', '政策', '流程', '规定', '费用']
        }

        for intent, keywords in intents.items():
            for keyword in keywords:
                if keyword in message:
                    return intent
        return 'general'

    def _build_prompt(self, user_message: str, history: List[Dict],
                      structured_context: str, knowledge: Dict,
                      waiting_info: Dict) -> str:
        print(f"\n🏗️ 开始构建Prompt...")
        print(f"   knowledge.has_knowledge: {knowledge.get('has_knowledge', False)}")

        system_prompt = """你是TWM旅行小程序的智能旅行助手，名字叫AI Dog。请遵循以下规则：
1. 基于提供的业务知识库信息回答用户问题
2. 如果知识库中有相关信息，优先使用知识库内容回答
3. 保持热情、专业的语气，像朋友一样推荐旅行建议
4. 回答简洁明了，直接解决用户问题
5. 如果需要更多信息才能解决问题，明确询问用户
6. 可以推荐景点、美食、路线、住宿等旅行相关内容
"""

        knowledge_section = ""
        if knowledge.get('has_knowledge'):
            knowledge_context = knowledge.get('context', '')
            print(f"   ✅ 知识库有内容，长度: {len(knowledge_context)} 字符")
            knowledge_section = f"""
【业务知识库】
{knowledge_context}
"""
        else:
            print(f"   ⚠️ 知识库为空！has_knowledge={knowledge.get('has_knowledge', False)}")
            knowledge_section = ""

        context_section = ""
        if structured_context:
            context_section = f"""
【用户上下文信息】
{structured_context}
"""

        waiting_section = ""
        if waiting_info.get('is_waiting'):
            fields = waiting_info['fields']
            waiting_section = f"""
【需要补充的信息】
当前正在等待用户提供：{', '.join([f['description'] for f in fields])}
"""

        history_section = ""
        if history:
            history_text = []
            for msg in history[-6:]:
                role = "用户" if msg['role'] == 'user' else "AI Dog"
                content = msg['content'][:200] if msg['content'] else ""
                history_text.append(f"{role}：{content}")
            history_section = f"""
【历史对话】
{chr(10).join(history_text)}
"""

        prompt = f"""{system_prompt}

{knowledge_section}

{context_section}

{waiting_section}

{history_section}

【用户当前问题】
{user_message}

请基于以上信息回答用户问题："""

        if knowledge_section:
            print(f"   📝 知识库部分预览: {knowledge_section[:200]}...")

        return prompt

    async def _call_llm(self, prompt: str, knowledge: Dict, user_message: str, session_id: str, user_id: str) -> str:
        if not Config.USE_MOCK_LLM and Config.LLM_API_URL and Config.LLM_API_KEY:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {Config.LLM_API_KEY}"
                }

                data = {
                    "model": Config.LLM_MODEL,
                    "messages": [
                        {"role": "system",
                         "content": "你是TWM旅行小程序的智能旅行助手AI Dog。请基于提供的知识库信息回答用户问题，回答要准确、友好、有帮助。可以推荐景点、美食、路线等旅行相关内容。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "stream": False
                }

                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        Config.LLM_API_URL,
                        json=data,
                        headers=headers
                    )

                    if response.status_code == 200:
                        result = response.json()
                        content = result['choices'][0]['message']['content']
                        print(f"✅ 智谱API返回成功，内容长度: {len(content)}")
                        return content
                    else:
                        print(f"❌ 智谱API返回错误: {response.status_code} - {response.text}")
                        return self._get_smart_mock_response(user_message, knowledge)

            except httpx.TimeoutException:
                print("❌ 智谱API超时")
                return self._get_smart_mock_response(user_message, knowledge)
            except Exception as e:
                print(f"❌ 智谱API调用失败: {e}")
                return self._get_smart_mock_response(user_message, knowledge)

        print("⚠️ 使用 Mock 响应模式")
        return self._get_smart_mock_response(user_message, knowledge)

    def _get_smart_mock_response(self, user_message: str, knowledge: Dict) -> str:
        if knowledge.get('has_knowledge'):
            context = knowledge.get('context', '')[:800]
            print(f"📚 使用知识库回答，上下文长度: {len(context)}")
            return f"🏞️ 根据TWM旅行助手的知识库：\n\n{context}\n\n以上信息来自我们的知识库，希望对您有帮助！"

        travel_keywords = ['景点', '好玩', '推荐', '去哪里', '旅游', '旅行', '路线', '攻略', '美食', '住宿']
        if any(k in user_message for k in travel_keywords):
            return """🏞️ 旅行目的地推荐：

根据热门旅行数据，以下是当前推荐的目的地：

1. **云南** - 四季如春，大理、丽江、香格里拉
2. **四川** - 九寨沟、稻城亚丁、成都美食
3. **海南** - 三亚沙滩、万宁冲浪
4. **北京** - 故宫、长城、胡同文化
5. **西安** - 兵马俑、大唐不夜城

您想去哪里？我可以帮您规划详细路线！"""

        else:
            return """🐕 您好！我是TWM旅行助手AI Dog！

我能为您提供：
🏞️ **旅行推荐** - 热门景点、小众目的地
🍜 **美食攻略** - 各地特色美食、餐厅推荐
🗺️ **路线规划** - 行程安排、交通建议
🏨 **住宿指南** - 酒店民宿推荐

请问您想了解什么？输入问题即可，我会尽力帮您解答！"""

    def _post_process(self, response: str, knowledge: Dict) -> str:
        return response