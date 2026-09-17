# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ========== 网络配置 ==========
    @staticmethod
    def disable_ssl_verify():
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

    # MySQL配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'twm_db')

    # 向量数据库配置
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './vector_db')

    # Embedding模型配置
    USE_EMBEDDING = True
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')

    # LLM配置（智谱AI）
    USE_MOCK_LLM = os.getenv('USE_MOCK_LLM', 'false').lower() == 'true'
    LLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_MODEL = "glm-4-flash"

    # RAG配置
    TOP_K_RETRIEVAL = 5
    MAX_CONTEXT_LENGTH = 4000

    SIMILARITY_THRESHOLDS = {
        'default': 0.55,
        '精确查询': 0.70,
        '景点详情': 0.60,
        '美食推荐': 0.55,
        '住宿建议': 0.55,
        '交通出行': 0.55,
        '安全提醒': 0.75,
        '紧急处理': 0.80,
        '习俗礼仪': 0.60,
        '购物攻略': 0.55,
        '最佳时间': 0.60,
        '路线规划': 0.60,
        '通用信息': 0.50
    }

    SIMILARITY_THRESHOLD = 0.55

    CONTEXT_EXPANSION_SIZE = 1
    ENABLE_RERANK = True
    RERANK_TOP_K = 10

    MAX_HISTORY_MESSAGES = 10
    SESSION_TIMEOUT = 3600

    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50