#!/usr/bin/env python3
"""
跨平台启动入口：检查依赖并启动美团打印机 Web 管理后台。
"""

import sys

from platform_utils import ensure_web_dependencies
from web_admin import run_server


def main():
    ok, message = ensure_web_dependencies()
    print(message)
    if not ok:
        print("Web 依赖安装失败，请检查 Python/pip 环境。")
        sys.exit(1)
    run_server()


if __name__ == "__main__":
    main()
