# knowledge/text_splitter.py
from typing import List, Dict, Optional
import re
import numpy as np
import hashlib


class TextSplitter:
    """
    智能文本分割器
    特性：
    1. 文档清洗（去除装饰符号、统一格式）
    2. 语义分片（基于embedding相似度）
    3. 保持语义完整性
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化文本分割器

        参数:
            chunk_size: 每个文本块的最大字符数
            chunk_overlap: 块之间的重叠字符数
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._embedding_model = None
        self._model_loaded = False

    def _get_embedding_model(self):
        """延迟加载 embedding 模型（用于语义分片）"""
        if self._model_loaded:
            return self._embedding_model

        try:
            from sentence_transformers import SentenceTransformer
            # 使用轻量级多语言模型
            self._embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self._model_loaded = True
            print("✅ 语义分片模型加载成功")
        except Exception as e:
            print(f"⚠️ 语义分片模型加载失败，将使用基础分片模式: {e}")
            self._embedding_model = None
            self._model_loaded = True

        return self._embedding_model

    def split(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        智能分片：清洗 -> 预分割 -> 语义合并

        返回: [{"content": "文本内容", "metadata": {...}}]
        """
        if not text or not text.strip():
            return []

        # 1. 清洗文本
        text = self._clean_text(text)

        if len(text) < 50:
            # 太短的文本直接作为一个片段
            result_meta = (metadata or {}).copy()
            result_meta['chunk_index'] = 0
            result_meta['chunk_hash'] = self._compute_hash(text)
            return [{'content': text, 'metadata': result_meta}]

        # 2. 按标题/段落预分割
        segments = self._pre_split_by_headers(text)

        # 3. 语义合并
        chunks = self._semantic_merge(segments)

        # 4. 格式化返回
        result = []
        for i, chunk in enumerate(chunks):
            chunk_meta = (metadata or {}).copy()
            chunk_meta['chunk_index'] = i
            chunk_meta['chunk_hash'] = self._compute_hash(chunk)
            chunk_meta['chunk_length'] = len(chunk)
            result.append({
                'content': chunk,
                'metadata': chunk_meta
            })

        return result

    def _clean_text(self, text: str) -> str:
        """
        清洗文本：去除装饰符号、统一格式、标准化空白
        """
        # 去除装饰性emoji和符号
        decor_chars = r'[✅❌⭐📝📍🔍🎯🏷️📢💡⚠️🚨🔔💬👍❤️💛💚💙💜🧡🖤🤍🤎]'
        text = re.sub(decor_chars, '', text)

        # 去除 Markdown 标题符号（保留文字内容）
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

        # 去除列表标记（数字点、短横、星号）
        text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[-*+]\s*', '', text, flags=re.MULTILINE)

        # 去除多余空格（保留一个空格）
        text = re.sub(r'[ \t]+', ' ', text)

        # 统一换行符：多个换行变成两个
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 去除首尾空白
        text = text.strip()

        return text

    def _pre_split_by_headers(self, text: str) -> List[str]:
        """
        按标题（##、###）和空行预分割
        将大文档切分为语义相对独立的段落组
        """
        lines = text.split('\n')
        segments = []
        current_segment = []

        for line in lines:
            stripped = line.strip()

            # 检测新标题（以##或###开头，或全大写标题）
            is_header = (
                    stripped.startswith('##') or
                    stripped.startswith('###') or
                    (stripped.isupper() and len(stripped) > 3 and len(stripped) < 30)
            )

            if is_header and current_segment:
                # 保存当前段落
                segment_text = '\n'.join(current_segment).strip()
                if segment_text:
                    segments.append(segment_text)
                current_segment = [line]
            else:
                current_segment.append(line)

        # 保存最后一个段落
        if current_segment:
            segment_text = '\n'.join(current_segment).strip()
            if segment_text:
                segments.append(segment_text)

        # 如果没有检测到标题，返回原文本作为单个段落
        if not segments and text:
            return [text]

        return segments

    def _semantic_merge(self, segments: List[str]) -> List[str]:
        """
        语义合并：计算相邻片段的语义相似度
        - 相似度高（>0.7）且长度允许 → 合并
        - 相似度低（<0.5） → 强制切分
        - 中间情况 → 参考长度因素
        """
        if len(segments) <= 1:
            return segments

        model = self._get_embedding_model()

        # 如果没有语义模型，回退到基础合并
        if model is None:
            return self._basic_merge(segments)

        try:
            # 计算所有片段的向量
            embeddings = model.encode(segments)
        except Exception as e:
            print(f"⚠️ 语义计算失败，回退到基础合并: {e}")
            return self._basic_merge(segments)

        chunks = []
        current_chunk = segments[0]

        for i in range(1, len(segments)):
            # 计算与上一个片段的相似度
            similarity = self._cosine_similarity(embeddings[i - 1], embeddings[i])

            # 预估合并后的长度
            merged_length = len(current_chunk) + len(segments[i]) + 1

            # 决策逻辑
            should_merge = False

            if similarity > 0.75:
                # 高度相似，尽量合并
                should_merge = merged_length <= self.chunk_size * 1.2
            elif similarity > 0.6:
                # 中度相似，长度允许则合并
                should_merge = merged_length <= self.chunk_size
            elif similarity > 0.45:
                # 低度相似，只有很短时才合并
                should_merge = merged_length <= self.chunk_size * 0.6
            else:
                # 语义差异大，强制切分
                should_merge = False

            if should_merge:
                current_chunk += "\n" + segments[i]
            else:
                # 保存当前块，开始新块
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = segments[i]

        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)

        # 后处理：确保没有块太长
        chunks = self._ensure_max_length(chunks)

        return chunks

    def _basic_merge(self, segments: List[str]) -> List[str]:
        """基础合并：按字符长度合并（不使用语义）"""
        chunks = []
        current_chunk = ""

        for seg in segments:
            # 预估合并后的长度
            merged_len = len(current_chunk) + len(seg) + (1 if current_chunk else 0)

            if merged_len <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n" + seg
                else:
                    current_chunk = seg
            else:
                # 保存当前块
                if current_chunk:
                    chunks.append(current_chunk)
                # 如果单个片段就超过限制，强制切分
                if len(seg) > self.chunk_size:
                    sub_chunks = self._force_split(seg)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = seg

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _force_split(self, text: str) -> List[str]:
        """强制切分超长文本（按句子边界）"""
        if len(text) <= self.chunk_size:
            return [text]

        # 按句子分割
        sentences = self._split_sentences(text)
        chunks = []
        current = ""

        for sent in sentences:
            if len(current) + len(sent) <= self.chunk_size:
                current += sent
            else:
                if current:
                    chunks.append(current)
                current = sent

        if current:
            chunks.append(current)

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """中文句子分割"""
        # 中文句子分隔符
        sentence_endings = re.compile(r'[。！？!?;；\n]')

        sentences = []
        start = 0

        for match in sentence_endings.finditer(text):
            end = match.end()
            sentence = text[start:end].strip()
            if sentence:
                sentences.append(sentence)
            start = end

        # 添加剩余内容
        if start < len(text):
            remaining = text[start:].strip()
            if remaining:
                sentences.append(remaining)

        return sentences

    def _ensure_max_length(self, chunks: List[str]) -> List[str]:
        """确保没有块超过最大长度限制"""
        result = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size * 1.2:
                result.append(chunk)
            else:
                # 超长块需要进一步切分
                sub_chunks = self._force_split(chunk)
                result.extend(sub_chunks)
        return result

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """计算两个向量的余弦相似度"""
        a_norm = a / (np.linalg.norm(a) + 1e-8)
        b_norm = b / (np.linalg.norm(b) + 1e-8)
        return float(np.dot(a_norm, b_norm))

    def _compute_hash(self, text: str) -> str:
        """计算文本哈希值（用于去重）"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]