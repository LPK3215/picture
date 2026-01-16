# 终端图像渲染器

将图片转换为终端彩色字符画的 Python 工具，支持多种渲染模式和可配置的模板系统。

## 功能特性

- 6 种内置渲染模板（像素映射、马赛克、半块高清、亮度字符、灰度、轮廓）
- 可配置的 Glyph 变体系统（10+ 种字符样式）
- 交互式模式 + 命令行模式
- 支持预览后再渲染全图
- 导出功能：PNG / HTML / ANSI 文本
- Windows/Linux/macOS 跨平台支持
- 纯配置文件扩展，无需修改代码

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 交互式模式

```bash
python main.py
```

流程：选择图片 → 选择模板 → 选择 Glyph → 预览 → 确认渲染 → 导出

### Web 模式 (Gradio)

```bash
python app.py
# 访问 http://localhost:7860
```

功能：上传图片、选择模板/Glyph、预览、导出 PNG/HTML

### 命令行模式

```bash
# 使用预设模板
python main.py data/bg2.jpg --preset PIXEL_RAW
python main.py data/bg2.jpg --preset HALF_HD --width 180
python main.py data/bg2.jpg --preset CHAR_LUMINANCE --glyph v3

# 兼容旧模式
python main.py data/bg2.jpg --mode bg --width 150
python main.py data/bg2.jpg --mode half --width 180
```

## 导出功能

渲染完成后可选择导出：

| 格式 | 说明 |
|------|------|
| PNG | 导出采样后的图像文件 |
| HTML | 可在浏览器中查看的彩色字符画 |
| ANSI | 包含转义序列的文本，可在终端回放 |

导出时会弹出系统"另存为"对话框（无 GUI 环境自动降级为命令行输入）。

ANSI 文件播放方式：
```bash
# Linux/macOS
cat output.ans

# Windows Terminal
type output.ans

# 带分页
less -R output.ans
```

## 预设模板

| ID | 名称 | 说明 | 默认宽度 |
|----|------|------|----------|
| `PIXEL_RAW` | 像素映射 | 彩色，最接近原图 | 150 |
| `PIXEL_MOSAIC` | 马赛克映射 | 彩色，电视信号效果 | 140 |
| `HALF_HD` | 半块映射 | 彩色，终端高清模式 | 180 |
| `CHAR_LUMINANCE` | 亮度字符 | 文本艺术风 | 120 |
| `GRAY_LEVEL` | 灰度映射 | DOS 风格 | 120 |
| `EDGE_STRUCTURE` | 轮廓映射 | 线稿素描风 | 120 |

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--preset, -p` | 预设模板 ID |
| `--glyph, -g` | Glyph 变体 ID (v1-v10) |
| `--mode, -m` | 兼容旧模式: fg/bg/half/mono |
| `--width, -w` | 输出宽度 |
| `--aspect, -a` | 宽高比校正 (默认 0.5) |
| `--delay, -d` | 每行延迟 (ms) |
| `--invert, -i` | 反转亮度 |
| `--clear` | 渲染前清屏 |

## 项目结构

```
picture/
├── main.py              # 程序入口
├── engine/
│   ├── __init__.py
│   ├── ansi.py          # ANSI 颜色工具
│   ├── preprocess.py    # 图像预处理
│   ├── modes.py         # 渲染模式实现
│   ├── renderer.py      # 渲染引擎
│   └── exporter.py      # 导出模块 (PNG/HTML/ANSI)
├── ui/
│   ├── __init__.py
│   ├── interactive.py   # 交互式界面
│   ├── preview.py       # 预览模块
│   └── save_dialog.py   # 保存对话框
├── config/
│   └── presets.json     # 模板与 Glyph 配置
├── data/
│   └── bg2.jpg          # 示例图片
├── requirements.txt
└── README.md
```

## 扩展指南

### 新增模板（只改配置）

编辑 `config/presets.json`，在 `semantic_templates` 数组中添加：

```json
{
  "id": "MY_TEMPLATE",
  "name": "我的模板",
  "desc": "自定义效果",
  "color_strategy": "truecolor",
  "mode": "pixel_raw",
  "defaults": {"width": 150, "aspect": 0.5},
  "glyph_family": "PixelBlock"
}
```

### 新增 Glyph 变体（只改配置）

编辑 `config/presets.json`，在对应的 `glyph_variants` 中添加：

```json
{
  "id": "v11",
  "name": "新变体",
  "desc": "描述",
  "glyph": "●"
}
```

## 依赖

- Python 3.8+
- Pillow >= 9.0.0
- colorama >= 0.4.0 (Windows)
- tkinter (可选，用于保存对话框)

## 许可

MIT License
