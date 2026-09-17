# start.py
import sys
import os
import multiprocessing

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn

    # 解决Windows上的多进程问题
    multiprocessing.freeze_support()

    print("=" * 60)
    print("🤖 智能客服系统启动中...")
    print("=" * 60)
    print("📡 API地址: http://0.0.0.0:8081")
    print("❤️  健康检查: http://localhost:8081/health")
    print("🔍 详细健康: http://localhost:8081/health/detailed")
    print("📚 API文档: http://localhost:8081/docs")
    print("=" * 60)

    # 关键：设置 reload=False 避免热重载冲突
    uvicorn.run(
        "api.routes:app",
        host="0.0.0.0",
        port=8081,
        reload=False,  # 重要：关闭热重载
        workers=1,  # 单进程模式
        log_level="info"
    )