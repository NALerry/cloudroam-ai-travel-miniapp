# api/routes.py - 简化稳定版
import asyncio
import time
import traceback
from fastapi import FastAPI, HTTPException, Form, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from service.chat_service import ChatService
from service.context_manager import ContextManager
from knowledge.knowledge_base import KnowledgeBaseManager
from database.mysql_client import MySQLClient
from config import Config

# ========== 创建应用 ==========
app = FastAPI(title="智能客服系统")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 全局超时和错误处理中间件 ==========
@app.middleware("http")
async def timeout_and_error_middleware(request: Request, call_next):
    """全局超时和错误处理中间件"""
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]

    # 设置超时时间（秒）
    timeout_seconds = 30

    try:
        # 使用超时控制
        response = await asyncio.wait_for(
            call_next(request),
            timeout=timeout_seconds
        )

        # 添加处理时间头
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        response.headers["X-Request-ID"] = request_id

        return response

    except asyncio.TimeoutError:
        process_time = time.time() - start_time
        print(f"⚠️ 请求超时 [{request_id}]: {request.method} {request.url.path} - {process_time:.2f}s")

        return JSONResponse(
            status_code=504,
            content={
                "success": False,
                "error": "请求处理超时，请稍后重试",
                "request_id": request_id,
                "path": request.url.path,
                "timeout_seconds": timeout_seconds
            }
        )

    except Exception as e:
        process_time = time.time() - start_time
        print(f"❌ 请求错误 [{request_id}]: {request.method} {request.url.path} - {str(e)}")
        print(traceback.format_exc())

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"服务器内部错误: {str(e)}",
                "request_id": request_id,
                "path": request.url.path
            }
        )


# ========== 初始化服务（同步方式，简单可靠） ==========
print("\n" + "=" * 60)
print("🚀 正在初始化服务...")
print("=" * 60)

try:
    print("📊 初始化数据库...")
    mysql = MySQLClient()
    print("✅ MySQL 初始化完成")
except Exception as e:
    print(f"❌ MySQL 初始化失败: {e}")
    mysql = None

try:
    print("📚 初始化知识库...")
    kb_manager = KnowledgeBaseManager()
    stats = kb_manager.get_stats()
    print(f"✅ 知识库初始化完成，共 {stats.get('total_chunks', 0)} 个块")
except Exception as e:
    print(f"❌ 知识库初始化失败: {e}")
    kb_manager = None

try:
    print("🔧 初始化上下文管理器...")
    context_manager = ContextManager()
    print("✅ 上下文管理器初始化完成")
except Exception as e:
    print(f"❌ 上下文管理器初始化失败: {e}")
    context_manager = None

try:
    print("💬 初始化聊天服务...")
    chat_service = ChatService()
    print("✅ 聊天服务初始化完成")
except Exception as e:
    print(f"❌ 聊天服务初始化失败: {e}")
    chat_service = None

print("=" * 60)
print("✅ 服务启动完成！")
print("📡 API文档: http://localhost:8081/docs")
print("=" * 60 + "\n")


# ========== 请求/响应模型 ==========
class SendMessageRequest(BaseModel):
    userId: str
    sessionId: Optional[str] = None
    message: str


class CreateSessionRequest(BaseModel):
    userId: str
    title: str = "新对话"


class AddDocumentRequest(BaseModel):
    filePath: str
    docName: Optional[str] = None


# ========== 健康检查端点 ==========
@app.get("/health")
async def health_check():
    """基础健康检查"""
    return {
        "status": "ok",
        "service": "customer_service",
        "timestamp": time.time(),
        "components": {
            "mysql": mysql is not None,
            "knowledge_base": kb_manager is not None,
            "chat_service": chat_service is not None
        }
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """详细健康检查"""
    results = {
        "status": "ok",
        "timestamp": time.time(),
        "components": {}
    }

    # 测试 MySQL
    try:
        if mysql:
            start = time.time()
            mysql.get_user_sessions("test", limit=1)
            results["components"]["mysql"] = {
                "status": "ok",
                "time_ms": round((time.time() - start) * 1000, 2)
            }
        else:
            results["components"]["mysql"] = {"status": "not_initialized"}
            results["status"] = "degraded"
    except Exception as e:
        results["components"]["mysql"] = {"status": "error", "error": str(e)}
        results["status"] = "degraded"

    # 测试知识库
    try:
        if kb_manager:
            start = time.time()
            stats = kb_manager.get_stats()
            results["components"]["knowledge_base"] = {
                "status": "ok",
                "chunks": stats.get("total_chunks", 0),
                "time_ms": round((time.time() - start) * 1000, 2)
            }
        else:
            results["components"]["knowledge_base"] = {"status": "not_initialized"}
            results["status"] = "degraded"
    except Exception as e:
        results["components"]["knowledge_base"] = {"status": "error", "error": str(e)}
        results["status"] = "degraded"

    return results


# ========== API端点 ==========

@app.post("/api/chat/session")
async def create_session(request: CreateSessionRequest):
    """创建新会话"""
    try:
        if mysql is None:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "数据库服务未就绪"}
            )

        session_id = str(uuid.uuid4())
        session_id = mysql.create_session(request.userId, session_id, request.title)

        return {
            "success": True,
            "data": {
                "sessionId": session_id,
                "userId": request.userId,
                "title": request.title
            }
        }
    except Exception as e:
        print(f"❌ 创建会话失败: {e}")
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}


@app.get("/api/chat/sessions")
async def get_sessions(userId: str):
    """获取用户所有会话"""
    try:
        if mysql is None:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "数据库服务未就绪"}
            )

        sessions = mysql.get_user_sessions(userId)
        return {"success": True, "data": sessions}
    except Exception as e:
        print(f"❌ 获取会话失败: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/chat/send")
async def send_message(request: SendMessageRequest):
    """发送消息"""
    try:
        if chat_service is None:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "聊天服务未就绪，请稍后重试"}
            )

        session_id = request.sessionId
        if not session_id and mysql:
            session_id = mysql.create_session(request.userId)
        elif not session_id:
            session_id = str(uuid.uuid4())

        try:
            result = await asyncio.wait_for(
                chat_service.process_message(
                    request.userId,
                    session_id,
                    request.message
                ),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            return {"success": False, "error": "消息处理超时，请稍后重试"}

        return {
            "success": True,
            "data": {
                "sessionId": session_id,
                "content": result.get('content', '处理失败'),
                "sources": result.get('sources', [])
            }
        }
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}


@app.get("/api/chat/history")
async def get_history(userId: str, sessionId: str, limit: int = 50):
    """获取聊天历史"""
    try:
        if mysql is None:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "数据库服务未就绪"}
            )

        messages = mysql.get_messages(sessionId, limit)
        return {
            "success": True,
            "data": {
                "sessionId": sessionId,
                "messages": messages
            }
        }
    except Exception as e:
        print(f"❌ 获取历史失败: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/knowledge/search")
async def search_knowledge(
        json_data: Optional[dict] = Body(None),
        query: Optional[str] = Form(None),
        top_k: int = Form(5)
):
    """搜索知识库"""
    try:
        if kb_manager is None:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "知识库服务未就绪"}
            )

        if json_data:
            search_query = json_data.get('query')
            search_top_k = json_data.get('top_k', top_k)
        else:
            search_query = query
            search_top_k = top_k

        if not search_query:
            return {
                "success": False,
                "error": "query参数不能为空",
                "usage": '请提供 query 参数'
            }

        results = kb_manager.search_knowledge(search_query, search_top_k)

        return {
            "success": True,
            "data": results,
            "meta": {
                "query": search_query,
                "top_k": search_top_k,
                "result_count": len(results)
            }
        }
    except Exception as e:
        print(f"❌ 知识库搜索失败: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/knowledge/search")
async def search_knowledge_get(query: str, top_k: int = 5):
    """GET 版本的搜索知识库"""
    try:
        if kb_manager is None:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "知识库服务未就绪"}
            )

        if not query:
            return {"success": False, "error": "query参数不能为空"}

        results = kb_manager.search_knowledge(query, top_k)

        return {
            "success": True,
            "data": results,
            "meta": {
                "query": query,
                "top_k": top_k,
                "result_count": len(results)
            }
        }
    except Exception as e:
        print(f"❌ GET搜索失败: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/knowledge/stats")
async def get_knowledge_stats():
    """获取知识库统计信息"""
    try:
        if kb_manager is None:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "知识库服务未就绪"}
            )

        stats = kb_manager.get_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        print(f"❌ 获取统计失败: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/context/{sessionId}")
async def get_session_context(sessionId: str):
    """获取会话的结构化上下文"""
    try:
        if mysql is None:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "数据库服务未就绪"}
            )

        context = mysql.get_session_context(sessionId)
        return {"success": True, "data": context}
    except Exception as e:
        print(f"❌ 获取上下文失败: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/feedback")
async def submit_feedback(sessionId: str, userId: str, rating: int, feedback: Optional[str] = None):
    """提交反馈"""
    try:
        if mysql is None:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "数据库服务未就绪"}
            )

        mysql.save_feedback(sessionId, userId, rating, feedback)
        return {"success": True, "message": "感谢您的反馈"}
    except Exception as e:
        print(f"❌ 提交反馈失败: {e}")
        return {"success": False, "error": str(e)}