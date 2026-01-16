#!/usr/bin/env python3
"""像素画生成器 - Web 入口"""

from src.web.app import create_app

if __name__ == "__main__":
    demo = create_app()
    demo.launch(server_name="0.0.0.0", server_port=7860)
