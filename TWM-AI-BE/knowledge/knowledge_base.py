# knowledge/knowledge_base.py
import os
from typing import List, Dict, Optional
from .document_loader import DocumentLoader
from .text_splitter import TextSplitter
from database.vector_client import VectorDBClient
from database.mysql_client import MySQLClient
from config import Config
import uuid
import re


class KnowledgeBaseManager:
    """
    知识库管理器 - 单例模式
    确保整个应用只有一个实例，避免索引加载问题
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 避免重复初始化
        if self._initialized:
            return

        self._initialized = True
        self._vector_db = None  # 延迟加载
        self._mysql = None
        self._doc_loader = None
        self._text_splitter = None

        print("✅ KnowledgeBaseManager 单例已创建")

    @property
    def vector_db(self):
        """延迟加载 VectorDBClient"""
        if self._vector_db is None:
            print("📥 延迟加载 VectorDBClient...")
            self._vector_db = VectorDBClient()
            # 打印加载状态
            stats = self._vector_db.get_collection_stats()
            print(f"   ✅ 加载完成，共 {stats.get('total_chunks', 0)} 个知识块")
        return self._vector_db

    @property
    def mysql(self):
        """延迟加载 MySQLClient"""
        if self._mysql is None:
            self._mysql = MySQLClient()
        return self._mysql

    @property
    def doc_loader(self):
        """延迟加载 DocumentLoader"""
        if self._doc_loader is None:
            self._doc_loader = DocumentLoader()
        return self._doc_loader

    @property
    def text_splitter(self):
        """延迟加载 TextSplitter"""
        if self._text_splitter is None:
            self._text_splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
        return self._text_splitter

    def add_document(self, file_path: str, doc_name: str = None) -> Dict:
        """
        添加文档到知识库（带清洗和语义分类）
        """
        doc_id = str(uuid.uuid4())
        doc_name = doc_name or os.path.basename(file_path)

        try:
            print(f"\n📄 开始处理文档: {doc_name}")

            # 1. 加载文档
            documents = self.doc_loader.load(file_path)
            print(f"   📖 加载完成，共 {len(documents)} 个原始文档块")

            # 2. 清洗 + 语义分片 + 分类
            all_chunks = []

            for doc_idx, doc in enumerate(documents):
                print(f"   🔄 处理文档块 {doc_idx + 1}/{len(documents)}...")

                # 使用语义分片器
                chunks = self.text_splitter.split(
                    doc['content'],
                    metadata={
                        'source': doc_name,
                        'doc_id': doc_id,
                        'type': doc.get('type', 'txt'),
                        'page': doc.get('page', 0),
                        'original_file': os.path.basename(file_path)
                    }
                )

                # 为每个片段添加语义分类和城市标签
                for chunk in chunks:
                    chunk['metadata']['semantic_class'] = self._classify_chunk(chunk['content'])
                    chunk['metadata']['city'] = self._extract_city(chunk['content'], doc_name)
                    chunk['metadata']['emergency_level'] = self._get_emergency_level(chunk['content'])

                all_chunks.extend(chunks)
                print(f"      ✅ 生成 {len(chunks)} 个知识片段")

            # 3. 去重（基于内容哈希）
            unique_chunks = self._deduplicate_chunks(all_chunks)
            print(f"   🗑️ 去重后剩余 {len(unique_chunks)} 个知识片段")

            # 4. 向量化并存储
            self.vector_db.add_documents(unique_chunks)

            return {
                'success': True,
                'doc_id': doc_id,
                'chunk_count': len(unique_chunks),
                'message': f'成功添加文档，共{len(unique_chunks)}个知识块',
                'doc_name': doc_name
            }

        except Exception as e:
            print(f"   ❌ 添加文档失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'doc_name': doc_name
            }

    def _classify_chunk(self, content: str) -> str:
        """
        对知识片段进行语义分类
        返回分类名称
        """
        classification_keywords = {
            '景点详情': ['景点', '景区', '游览', '门票', '开放时间', '建议游玩', '必去', '打卡', '风光', '名胜'],
            '美食推荐': ['美食', '餐厅', '小吃', '推荐店铺', '火锅', '烤鸭', '好吃', '味道', '必吃', '早茶', '夜宵'],
            '住宿建议': ['住宿', '酒店', '民宿', '青年旅舍', '房价', '入住', '房间', '客栈', '宾馆'],
            '交通出行': ['交通', '地铁', '公交', '打车', '机场', '火车站', '自驾', '高铁', '航班', '路况', '乘车'],
            '安全提醒': ['安全', '防盗', '报警', '急救', '保险', '小心', '注意', '危险', '防范', '骗局'],
            '习俗礼仪': ['习俗', '礼仪', '禁忌', '文化', '信仰', '尊重', '风俗', '传统', '规矩', '忌讳'],
            '紧急处理': ['紧急', '丢失', '事故', '报警', '急救', '领事馆', '救护车', '火警', '求助'],
            '购物攻略': ['购物', '买', '特产', '免税', '退税', '价格', '商场', '纪念品', '伴手礼'],
            '最佳时间': ['最佳旅游时间', '季节', '天气', '气候', '月份', '旺季', '淡季', '赏花', '红叶'],
            '路线规划': ['路线', '行程', '规划', '推荐路线', '一日游', '几日游', '行程安排']
        }

        for class_name, keywords in classification_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    return class_name
        return '通用信息'

    def _extract_city(self, content: str, file_name: str) -> str:
        """提取城市信息"""
        city_keywords = {
            '北京': ['北京', '故宫', '长城', '天坛', '颐和园', '鸟巢'],
            '上海': ['上海', '外滩', '东方明珠', '迪士尼', '南京路', '豫园'],
            '成都': ['成都', '熊猫', '宽窄巷子', '锦里', '都江堰', '青城山'],
            '西安': ['西安', '兵马俑', '大雁塔', '城墙', '回民街', '钟楼'],
            '杭州': ['杭州', '西湖', '灵隐寺', '雷峰塔', '西溪', '龙井'],
            '三亚': ['三亚', '天涯海角', '亚龙湾', '蜈支洲岛', '海棠湾', '南山'],
            '云南': ['云南', '大理', '丽江', '香格里拉', '西双版纳', '洱海'],
            '桂林': ['桂林', '漓江', '阳朔', '象鼻山', '龙脊梯田'],
            '厦门': ['厦门', '鼓浪屿', '厦大', '环岛路', '曾厝垵'],
            '南京': ['南京', '中山陵', '夫子庙', '总统府', '玄武湖'],
            '重庆': ['重庆', '洪崖洞', '解放碑', '磁器口', '火锅'],
            '长沙': ['长沙', '岳麓山', '橘子洲', '臭豆腐', '茶颜悦色'],
            '武汉': ['武汉', '黄鹤楼', '东湖', '武大', '热干面'],
            '青岛': ['青岛', '栈桥', '八大关', '崂山', '啤酒'],
            '香港': ['香港', '维多利亚港', '迪士尼', '太平山', '旺角'],
            '澳门': ['澳门', '大三巴', '威尼斯人', '蛋挞'],
            '台北': ['台北', '101', '士林夜市', '九份'],
            '日本': ['日本', '东京', '大阪', '京都', '北海道', '富士山'],
            '泰国': ['泰国', '曼谷', '清迈', '普吉', '芭堤雅'],
            '韩国': ['韩国', '首尔', '釜山', '济州岛'],
            '新加坡': ['新加坡', '鱼尾狮', '滨海湾', '圣淘沙'],
            '法国': ['法国', '巴黎', '埃菲尔铁塔', '卢浮宫', '普罗旺斯'],
            '意大利': ['意大利', '罗马', '威尼斯', '佛罗伦萨', '米兰'],
            '英国': ['英国', '伦敦', '大本钟', '剑桥', '牛津'],
            '美国': ['美国', '纽约', '洛杉矶', '旧金山', '拉斯维加斯']
        }

        for city in city_keywords.keys():
            if city in file_name:
                return city

        for city, keywords in city_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    return city
        return '通用'

    def _get_emergency_level(self, content: str) -> int:
        """获取紧急程度（0-3）"""
        emergency_keywords = {
            3: ['紧急', '急救', '报警', '火警', '丢失证件', '被盗', '抢劫', '突发疾病'],
            2: ['警告', '注意安全', '禁止', '危险', '小心', '防骗', '防盗'],
            1: ['建议', '提醒', '最好不要', '避免', '注意']
        }

        for level, keywords in emergency_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    return level
        return 0

    def _deduplicate_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """去重：基于内容哈希"""
        seen_hashes = set()
        unique_chunks = []

        for chunk in chunks:
            chunk_hash = chunk['metadata'].get('chunk_hash', '')
            if chunk_hash and chunk_hash not in seen_hashes:
                seen_hashes.add(chunk_hash)
                unique_chunks.append(chunk)
            elif not chunk_hash:
                content_preview = chunk['content'][:100]
                if content_preview not in seen_hashes:
                    seen_hashes.add(content_preview)
                    unique_chunks.append(chunk)
        return unique_chunks

    def search_knowledge(self, query: str, top_k: int = 5,
                         filter_city: str = None,
                         filter_class: str = None) -> List[Dict]:
        """
        检索相关知识（支持过滤）
        """
        # 强制刷新确保数据最新
        results = self.vector_db.search(query, top_k * 2)

        filtered = []
        for r in results:
            similarity = r.get('similarity', 0)
            if similarity < Config.SIMILARITY_THRESHOLD:
                continue

            meta = r.get('metadata', {})
            if filter_city and meta.get('city') != filter_city:
                continue
            if filter_class and meta.get('semantic_class') != filter_class:
                continue

            filtered.append(r)

        return filtered[:top_k]

    def get_relevant_context(self, query: str, filter_city: str = None) -> str:
        """获取相关的知识上下文"""
        results = self.search_knowledge(query, filter_city=filter_city)

        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results):
            source = result['metadata'].get('source', '未知来源')
            city = result['metadata'].get('city', '')
            semantic_class = result['metadata'].get('semantic_class', '')
            content = result['content']
            similarity = result.get('similarity', 0)

            location_info = f"[{city}]" if city else ""
            class_info = f"({semantic_class})" if semantic_class else ""

            context_parts.append(
                f"【知识{i + 1}】{location_info}{class_info} 来源：{source} 相关度：{similarity:.2f}\n{content}\n"
            )

        return "\n".join(context_parts)

    def get_stats(self) -> Dict:
        """获取知识库统计信息"""
        stats = self.vector_db.get_collection_stats()
        sources = self.vector_db.list_sources()

        return {
            "total_chunks": stats.get("total_chunks", 0),
            "sources": sources,
            "status": "active",
            "vector_dimension": stats.get("vector_dimension", 0)
        }

    def reload(self):
        """强制重新加载向量数据库"""
        print("🔄 强制重新加载向量数据库...")
        if self._vector_db is not None:
            # 重新初始化
            self._vector_db = None
        _ = self.vector_db  # 触发重新加载
        print("   ✅ 重新加载完成")