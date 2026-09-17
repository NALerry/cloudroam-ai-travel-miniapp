# service/rag_service.py
from typing import Dict, List
from knowledge.knowledge_base import KnowledgeBaseManager
from config import Config
import traceback


class RAGService:
    def __init__(self):
        self.kb_manager = KnowledgeBaseManager()
        # 添加诊断信息
        stats = self.kb_manager.get_stats()
        print(f"📊 RAGService 初始化，知识库状态: {stats.get('total_chunks', 0)} 个块")

    async def retrieve_context(self, query: str) -> Dict:
        """
        检索相关知识
        返回: {
            'has_knowledge': bool,
            'context': str,
            'sources': List[Dict]
        }
        """
        print(f"\n{'=' * 50}")
        print(f"🔍 RAG检索开始")
        print(f"   查询: {query}")
        print(f"   TOP_K: {Config.TOP_K_RETRIEVAL}")
        print(f"   相似度阈值: {Config.SIMILARITY_THRESHOLD}")
        print(f"{'=' * 50}")

        try:
            # 添加诊断：检查知识库状态
            stats = self.kb_manager.get_stats()
            print(f"📊 当前知识库状态: {stats.get('total_chunks', 0)} 个块")

            if stats.get('total_chunks', 0) == 0:
                print("⚠️ 知识库为空！请先上传文档")
                return {
                    'has_knowledge': False,
                    'context': '',
                    'sources': []
                }

            results = self.kb_manager.search_knowledge(query, top_k=Config.TOP_K_RETRIEVAL)

            print(f"📊 检索结果数量: {len(results)}")

            if results:
                for i, r in enumerate(results[:3]):
                    print(f"   结果{i + 1}: 相似度={r.get('similarity', 0):.4f}")
                    print(f"   来源: {r['metadata'].get('source', '未知')}")
                    print(f"   内容预览: {r['content'][:100]}...")
            else:
                print("⚠️ 没有检索到相关知识")
                return {
                    'has_knowledge': False,
                    'context': '',
                    'sources': []
                }

            # 构建上下文
            context_parts = []
            sources = []

            for i, result in enumerate(results):
                source = result['metadata'].get('source', '未知来源')
                similarity = result.get('similarity', 0)

                # 只保留相似度高于阈值的结果
                if similarity < Config.SIMILARITY_THRESHOLD:
                    print(f"   跳过结果{i + 1}: 相似度{similarity:.4f} < 阈值{Config.SIMILARITY_THRESHOLD}")
                    continue

                context_parts.append(
                    f"【知识片段{i + 1}】（来源：{source}，相关度：{similarity:.2f}）\n{result['content']}\n"
                )

                sources.append({
                    'source': source,
                    'similarity': similarity,
                    'content_preview': result['content'][:200]
                })

            if not context_parts:
                print("⚠️ 所有结果都被相似度阈值过滤掉了")
                return {
                    'has_knowledge': False,
                    'context': '',
                    'sources': []
                }

            result = {
                'has_knowledge': True,
                'context': '\n'.join(context_parts),
                'sources': sources
            }

            print(f"✅ RAG检索成功，找到 {len(sources)} 个知识片段")
            print(f"📝 上下文长度: {len(result['context'])} 字符")

            return result

        except Exception as e:
            print(f"❌ RAG检索异常: {e}")
            print(traceback.format_exc())
            return {
                'has_knowledge': False,
                'context': '',
                'sources': []
            }

    async def enrich_with_knowledge(self, query: str, user_context: str = "") -> str:
        """
        使用知识库增强查询
        """
        retrieval_result = await self.retrieve_context(query)

        if not retrieval_result['has_knowledge']:
            return user_context

        # 组合上下文
        enhanced = f"""
## 业务知识库信息
以下是相关业务知识，请基于这些知识回答用户问题：

{retrieval_result['context']}

## 用户历史对话上下文
{user_context}
"""
        return enhanced