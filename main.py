"""主程序入口"""

import uvicorn
from backend.utils.config import settings


def main():
    """启动应用"""
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )


if __name__ == "__main__":
    main()
