# 像素画生成器

将图片转换为像素风格字符画的 Python 工具，支持多种渲染模式和可配置的模板系统。

## 功能特性

- 6 种内置渲染模板（像素映射、马赛克、半块高清、亮度字符、灰度、轮廓）
- 可配置的字符样式系统（10+ 种字符样式）
- Web 界面 + CLI 交互模式 + 命令行模式
- 导出功能：PNG 字符画图像 / HTML / ANSI 文本
- 响应式 Web 界面，支持移动端
- 纯配置文件扩展，无需修改代码

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### Web 模式（推荐）

```bash
python app.py
# 访问 http://localhost:7860
```

### CLI 交互模式

```bash
python main.py
```

### 命令行模式

```bash
python main.py data/bg2.jpg --preset PIXEL_RAW
python main.py data/bg2.jpg --preset HALF_HD --width 180
python main.py data/bg2.jpg --preset CHAR_LUMINANCE --glyph v3
```

## 预设模板

| ID | 名称 | 说明 | 默认宽度 |
|----|------|------|----------|
| `PIXEL_RAW` | 像素映射 | 彩色，最接近原图 | 150 |
| `PIXEL_MOSAIC` | 马赛克映射 | 彩色，电视信号效果 | 140 |
| `HALF_HD` | 半块映射 | 彩色，高清模式 | 180 |
| `CHAR_LUMINANCE` | 亮度字符 | 文本艺术风 | 120 |
| `GRAY_LEVEL` | 灰度映射 | DOS 风格 | 120 |
| `EDGE_STRUCTURE` | 轮廓映射 | 线稿素描风 | 120 |

## 导出功能

| 格式 | 说明 |
|------|------|
| PNG | 将字符画渲染为图像文件 |
| HTML | 可在浏览器中查看的彩色字符画 |
| ANSI | 包含转义序列的文本，可在终端回放 |

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--preset, -p` | 预设模板 ID |
| `--glyph, -g` | 字符样式 ID（因模板而异） |
| `--width, -w` | 输出宽度 |
| `--aspect, -a` | 宽高比校正 (默认 0.5) |
| `--delay, -d` | 每行延迟 (ms) |
| `--invert, -i` | 反转亮度 |
| `--clear` | 渲染前清屏 |

## 项目结构

```
picture/
├── main.py              # CLI 入口
├── app.py               # Web 入口
├── src/                 # 核心代码
│   ├── engine/          # 渲染引擎
│   │   ├── ansi.py      # ANSI 颜色工具
│   │   ├── preprocess.py# 图像预处理
│   │   ├── modes.py     # 渲染模式实现
│   │   ├── renderer.py  # 配置管理与渲染调度
│   │   └── exporter.py  # 导出模块
│   ├── ui/              # CLI 交互界面
│   └── web/             # Web 应用
│       └── app.py       # Gradio 界面
├── config/
│   └── presets.json     # 模板与字符样式配置
├── data/
│   └── bg2.jpg          # 示例图片
└── requirements.txt
```

## 扩展指南

### 新增模板

编辑 `config/presets.json`，在 `semantic_templates` 数组中添加：

```json
{
  "id": "MY_TEMPLATE",
  "name": "我的模板",
  "desc": "自定义效果",
  "mode": "pixel_raw",
  "defaults": {"width": 150, "aspect": 0.5},
  "glyph_family": "PixelBlock"
}
```

### 新增字符样式

编辑 `config/presets.json`，在对应的 `glyph_variants` 中添加：

```json
{
  "id": "v11",
  "name": "新样式",
  "desc": "描述",
  "glyph": "●"
}
```

## 依赖

- Python 3.8+
- Pillow >= 9.0.0
- Gradio >= 4.0.0
- colorama >= 0.4.0 (Windows)

## 许可

MIT License
