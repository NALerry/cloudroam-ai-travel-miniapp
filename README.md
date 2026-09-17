# 云游志微信小程序

> 面向旅行爱好者的“发现-规划-记录-分享”一站式微信小程序，集成 AI Dog 智能助手。

🏆 **传智杯全国 IT 技能大赛——AI 微信小程序开发挑战赛 国赛（B 组）三等奖**


## 功能特性

- **发现页**：搜索、分类导航（出行/住宿/美食/习俗/购物）、旅行安全提示、AI 助手入口
- **地图页**：地点搜索、路线规划、天气查看、网友攻略
- **天气页**：实时天气、24 小时预报、未来 7 天预报、生活指数
- **社区页**：图文发布、点赞、收藏、评论、搜索
- **个人中心**：资料管理、我的投稿/收藏/点赞/浏览历史、地点收藏、我的路线、旅行笔记
- **AI Dog 智能助手**：基于 RAG 的自然语言问答、行程建议、目的地信息、功能指引

## 技术栈

- **前端**：uni-app、Vue.js、uni-ui
- **业务后端**：Spring Boot 2.7+（Java 17）、Spring Data JPA、MySQL 8.0
- **AI 服务**：Python FastAPI、RAG、FAISS、paraphrase-multilingual-MiniLM-L12-v2、智谱 AI GLM-4-Flash
- **第三方 API**：腾讯地图 API、心知天气 API
- **其他**：JWT、RESTful API、多端适配

## 系统架构

```text
前端（uni-app 微信小程序）
   │
   ├── Spring Boot 业务后端 ── MySQL 8.0
   │
   └── Python FastAPI AI 服务 ── FAISS 向量库 / 智谱 GLM-4-Flash
```

Spring Boot 负责用户、帖子、互动、文件等核心业务；Python FastAPI 独立支撑 AI Dog 智能助手，基于 RAG 架构实现知识库问答。二者独立部署、接口交互，具备良好的扩展性与维护性。

## 快速开始

### 环境要求

- 微信开发者工具 / HBuilderX
- JDK 17+
- MySQL 8.0+
- Python 3.9+

### 后端启动

```bash
# Spring Boot 业务后端
cd TWM-BE
mvn spring-boot:run

# Python AI 服务
cd TWM-AI-BE
pip install -r requirements.txt
python main.py
```

### 前端启动

1. 使用 HBuilderX 打开 `TWM-FE/` 目录。
2. 在请求配置中修改后端地址：

```javascript
const BASE_URL = 'http://localhost:8080'
const AI_BASE_URL = 'http://localhost:8081'

## 目录结构

```text
├── TWM-FE/         # uni-app 前端
├── TWM-BE/         # Spring Boot 业务后端
├── TWM-AI-BE/      # Python FastAPI AI 服务
├── docs/           # 说明文档
├── videos/         # 项目演示视频
└── README.md
```

## 核心实现

- **AI Dog 智能助手**：基于 RAG 检索增强生成，结合 FAISS 向量库与智谱 GLM-4-Flash，提升回答准确性与实用性。
- **双服务架构**：Spring Boot 业务后端与 Python AI 服务解耦，便于扩展、部署和维护。
- **多端适配**：uni-app 一套代码发布微信小程序、H5、App。
- **第三方 API 集成**：腾讯地图、心知天气，支持路线规划与实时天气查询。

## 项目成果

- 传智杯全国 IT 技能大赛——AI 微信小程序开发挑战赛 国赛（B 组）三等奖

## 详细文档

- [项目介绍文档](docs/项目介绍文档.docx)
