# knowledge/document_loader.py
from typing import List, Dict
import os
from bs4 import BeautifulSoup
import requests

# 尝试导入PDF处理库，如果失败则给出提示
try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("警告: PyPDF2 未安装，无法处理PDF文件")

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    print("警告: python-docx 未安装，无法处理Word文件")


class DocumentLoader:
    def load(self, file_path: str) -> List[Dict]:
        """根据文件类型加载文档"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            if not HAS_PYPDF2:
                raise ImportError("请安装 PyPDF2: pip install PyPDF2")
            return self._load_pdf(file_path)
        elif ext == '.docx':
            if not HAS_DOCX:
                raise ImportError("请安装 python-docx: pip install python-docx")
            return self._load_docx(file_path)
        elif ext == '.txt':
            return self._load_txt(file_path)
        elif ext == '.html':
            return self._load_html(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {ext}")

    def load_from_url(self, url: str) -> List[Dict]:
        """从URL加载HTML文档"""
        response = requests.get(url)
        response.encoding = 'utf-8'
        return self._load_html_from_text(response.text, source=url)

    def _load_pdf(self, file_path: str) -> List[Dict]:
        documents = []
        reader = PdfReader(file_path)

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                documents.append({
                    'content': text,
                    'page': page_num + 1,
                    'type': 'pdf'
                })
        return documents

    def _load_docx(self, file_path: str) -> List[Dict]:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)

        return [{
            'content': '\n'.join(full_text),
            'page': 0,
            'type': 'docx'
        }]

    def _load_txt(self, file_path: str) -> List[Dict]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()

        return [{
            'content': content,
            'page': 0,
            'type': 'txt'
        }]

    def _load_html(self, file_path: str) -> List[Dict]:
        with open(file_path, 'r', encoding='utf-8') as f:
            return self._load_html_from_text(f.read())

    def _load_html_from_text(self, html_text: str, source: str = None) -> List[Dict]:
        soup = BeautifulSoup(html_text, 'html.parser')

        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return [{
            'content': text,
            'page': 0,
            'type': 'html',
            'source': source
        }]