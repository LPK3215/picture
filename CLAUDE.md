# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

像素画生成器 - 将图片转换为像素风格字符画的 Python 工具，支持 6 种渲染模板、10+ 种字符样式，提供 Web 界面、CLI 交互模式和命令行模式。

## 常用命令

### 运行应用

```bash
# Web 模式（推荐）- 启动 Gradio Web 界面
python app.py
# 访问 http://localhost:7860

# CLI 交互模式 - 无参数启动进入交互式会话
python main.py

# 命令行模式 - 直接渲染
python main.py data/bg2.jpg --preset PIXEL_RAW --width 150
python main.py <图片路径> --preset <预设ID> --glyph <样式ID> --width <宽度>
```

### 依赖管理

```bash
# 安装依赖
pip install -r requirements.txt
```

### 部署

```bash
# Docker 部署
cd deploy
docker-compose up -d

# 系统服务部署
sudo cp deploy/pixel-art.service /etc/systemd/system/
sudo systemctl start pixel-art
```

## 核心架构

### 模块结构

- **src/engine/** - 渲染引擎核心
  - `renderer.py` - 配置管理器 (Config) 和渲染调度器 (Renderer)
  - `modes.py` - 6 种渲染模式实现 (MODE_REGISTRY)
  - `preprocess.py` - 图像预处理 (缩放、裁剪、马赛克、边缘检测)
  - `ansi.py` - ANSI 终端颜色工具
  - `exporter.py` - 导出功能 (PNG/HTML/ANSI)

- **src/ui/** - CLI 交互界面
  - `interactive.py` - 交互式会话
  - `preview.py` - 终端预览
  - `save_dialog.py` - 保存对话框

- **src/web/** - Web 应用
  - `app.py` - Gradio 界面 (PixelArtApp 类)

- **config/presets.json** - 模板和字符样式配置文件

### 渲染流程

1. **加载配置** - Config 从 `config/presets.json` 读取模板和字符样式
2. **图像加载** - Renderer.load_image() 加载并转换为 RGB
3. **图像预处理** - prepare_image() 根据模式调整尺寸和宽高比（half_hd 模式会自动将 aspect * 2）
4. **模式渲染** - 根据 template["mode"] 从 MODE_REGISTRY 获取渲染函数
5. **输出** - 终端直接打印 (return_lines=False) 或返回行数据 (return_lines=True)

### 6 种渲染模式

| 模式 ID | 函数 | 说明 |
|---------|------|------|
| `pixel_raw` | render_pixel_raw | 背景色块，最接近原图 |
| `pixel_mosaic` | render_pixel_mosaic | 马赛克效果 (2x2 区域平均) |
| `half_hd` | render_half_hd | 半块字符 (▀/▄)，上下两像素合并 |
| `char_luminance` | render_char_luminance | 亮度映射到字符集 |
| `gray_level` | render_gray_level | 灰度字符 |
| `edge_structure` | render_edge_structure | 边缘检测线稿 |

### 配置系统

**config/presets.json** 包含三个主要部分：

1. **semantic_templates** - 渲染模板定义
   - `id` - 模板唯一标识
   - `mode` - 渲染模式 (对应 MODE_REGISTRY)
   - `glyph_family` - 关联的字符样式族
   - `defaults` - 默认参数 (width, aspect, invert 等)

2. **glyph_variants** - 字符样式族定义
   - 每个族包含多个 variants
   - `glyph` - 单字符 (用于像素/半块模式)
   - `charset` - 字符集 (用于亮度/灰度模式)

3. **legacy_mode_mapping** - 旧版模式兼容映射

### Web 应用架构

- **PixelArtApp** - 主应用类，封装所有业务逻辑
- **render_to_html_data()** - 将图像渲染为 HTML span 标签和字符数据（在 modes.py 中）
- **尺寸限制** - MAX_WIDTH=300（防止浏览器卡顿），图像自动限制到 6000px
- **导出功能** - PNG (字符画图像)、HTML (可浏览器查看)
- **响应式布局** - 支持桌面和移动端

### CLI 交互模式

无参数运行 `python main.py` 时进入交互模式，循环调用 `interactive_session()`，提供预览、参数调整、保存等功能。

## 扩展指南

### 添加新渲染模式

1. 在 `src/engine/modes.py` 中实现渲染函数
2. 注册到 MODE_REGISTRY
3. 在 `config/presets.json` 中添加使用该模式的模板
4. 如需 Web 支持，在 `render_to_html_data()` 中添加对应逻辑

### 添加新模板

编辑 `config/presets.json` 的 `semantic_templates` 数组，无需修改代码。

### 添加新字符样式

编辑 `config/presets.json` 的 `glyph_variants` 对应族，无需修改代码。

## 技术栈

- Python 3.8+
- Pillow - 图像处理
- Gradio 4.0+ - Web 界面
- colorama - Windows 终端颜色支持
