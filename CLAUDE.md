# CLAUDE.md

## 项目概述

终端图像渲染器 - 将图片转换为终端彩色字符画的 Python 工具。

## 功能

- 6 种渲染模板（像素映射、马赛克、半块高清、亮度字符、灰度、轮廓）
- 可配置的 Glyph 变体系统
- CLI 交互模式 + 命令行模式 + Web 模式 (Gradio)
- 导出 PNG / HTML / ANSI

## 运行

```bash
# CLI 交互模式
python main.py

# 命令行模式
python main.py data/bg2.jpg --preset HALF_HD --width 180

# Web 模式
python app.py
```

## 项目结构

- `main.py` - CLI 入口
- `app.py` - Gradio Web 入口
- `engine/` - 渲染引擎（modes.py, renderer.py, exporter.py）
- `ui/` - 交互界面
- `config/presets.json` - 模板配置

## 扩展

新增模板/Glyph 只需修改 `config/presets.json`，无需改代码。
