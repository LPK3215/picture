#!/usr/bin/env python3
"""
终端图像渲染器 - Gradio Web 应用

启动方式：
    python app.py
    访问 http://localhost:7860
"""

import tempfile
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import gradio as gr

from engine.renderer import Config, Renderer
from engine.preprocess import resize, center_crop, brightness

# ============ 配置加载 ============
CONFIG_PATH = Path(__file__).parent / "config" / "presets.json"
config = Config(CONFIG_PATH)
renderer = Renderer(config)

# 最大渲染宽度
MAX_WIDTH = 300
PREVIEW_WIDTH = 180

# 字符画渲染参数
CHAR_WIDTH = 8
CHAR_HEIGHT = 14


def get_template_choices():
    """获取模板下拉选项"""
    return [(f"{t['name']} - {t['desc']}", t['id']) for t in config.templates]


def get_glyph_choices(template_id: str):
    """根据模板获取 glyph 下拉选项"""
    template = config.get_template(template_id)
    if not template:
        return [("默认", "default")]

    family_id = template.get("glyph_family", "")
    family = config.get_glyph_family(family_id)
    if not family or not family.get("variants"):
        return [("默认", "default")]

    choices = []
    default_id = family.get("default", "v1")

    for v in family["variants"]:
        glyph = v.get("glyph", "")
        charset = v.get("charset", "")

        if glyph:
            sample = glyph * 16
            label = f"{v['name']}  {sample}"
        elif charset:
            sample = charset[:16]
            label = f"{v['name']}  [{sample}]"
        else:
            label = v['name']

        if v["id"] == default_id:
            label += " (默认)"

        choices.append((label, v["id"]))

    return choices


def limit_image_size(img: Image.Image, max_size: int = 6000) -> Image.Image:
    """限制图片尺寸，防止 OOM"""
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return img


def render_to_html_lines(img: Image.Image, template: dict, glyph_variant: dict,
                         width: int) -> tuple:
    """渲染图片为 HTML 行，同时返回字符数据用于 PNG 导出"""
    mode = template.get("mode", "pixel_raw")
    aspect = template.get("defaults", {}).get("aspect", 0.5)

    if mode == "half_hd":
        aspect = aspect * 2

    img = resize(img, width, aspect)
    pixels = img.load()
    w, h = img.size

    glyph = glyph_variant.get("glyph", "█") if glyph_variant else "█"
    charset = glyph_variant.get("charset", "") if glyph_variant else ""

    html_lines = []
    char_data = []  # [(char, r, g, b, bg_r, bg_g, bg_b), ...]

    if mode == "half_hd":
        half_glyph = glyph if glyph in ("▀", "▄") else "▀"
        for y in range(0, h - 1, 2):
            line = ""
            row_data = []
            for x in range(w):
                r1, g1, b1 = pixels[x, y]
                r2, g2, b2 = pixels[x, min(y + 1, h - 1)]
                if half_glyph == "▀":
                    line += f'<span style="color:rgb({r1},{g1},{b1});background:rgb({r2},{g2},{b2})">▀</span>'
                    row_data.append(("▀", r1, g1, b1, r2, g2, b2))
                else:
                    line += f'<span style="color:rgb({r2},{g2},{b2});background:rgb({r1},{g1},{b1})">▄</span>'
                    row_data.append(("▄", r2, g2, b2, r1, g1, b1))
            html_lines.append(line)
            char_data.append(row_data)
    elif charset:
        for y in range(h):
            line = ""
            row_data = []
            for x in range(w):
                r, g, b = pixels[x, y]
                br = brightness(r, g, b)
                idx = int(br * (len(charset) - 1))
                char = charset[min(idx, len(charset) - 1)]
                esc_char = char
                if char == '<':
                    esc_char = '&lt;'
                elif char == '>':
                    esc_char = '&gt;'
                elif char == '&':
                    esc_char = '&amp;'
                elif char == ' ':
                    esc_char = '&nbsp;'
                line += f'<span style="color:rgb({r},{g},{b})">{esc_char}</span>'
                row_data.append((char, r, g, b, 30, 30, 30))
            html_lines.append(line)
            char_data.append(row_data)
    else:
        for y in range(h):
            line = ""
            row_data = []
            for x in range(w):
                r, g, b = pixels[x, y]
                line += f'<span style="color:rgb({r},{g},{b})">{glyph}</span>'
                row_data.append((glyph, r, g, b, 30, 30, 30))
            html_lines.append(line)
            char_data.append(row_data)

    return html_lines, char_data


def render_char_to_png(char_data: list, output_path: str):
    """将字符数据渲染为 PNG 图像"""
    if not char_data or not char_data[0]:
        return False

    rows = len(char_data)
    cols = len(char_data[0])

    img_width = cols * CHAR_WIDTH
    img_height = rows * CHAR_HEIGHT

    img = Image.new('RGB', (img_width, img_height), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    # 尝试加载等宽字体
    try:
        font = ImageFont.truetype("consola.ttf", 12)
    except:
        try:
            font = ImageFont.truetype("DejaVuSansMono.ttf", 12)
        except:
            font = ImageFont.load_default()

    for y, row in enumerate(char_data):
        for x, (char, r, g, b, bg_r, bg_g, bg_b) in enumerate(row):
            px = x * CHAR_WIDTH
            py = y * CHAR_HEIGHT
            # 绘制背景
            draw.rectangle([px, py, px + CHAR_WIDTH, py + CHAR_HEIGHT],
                           fill=(bg_r, bg_g, bg_b))
            # 绘制字符
            draw.text((px, py), char, fill=(r, g, b), font=font)

    img.save(output_path, "PNG")
    return True


def wrap_html(lines: list, title: str = "Terminal Art") -> str:
    """包装为完整 HTML"""
    content = "\n".join(lines)
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ background-color: #1e1e1e; margin: 20px; }}
        pre {{ font-family: Consolas, Monaco, 'Courier New', monospace; font-size: 12px; line-height: 1.0; }}
    </style>
</head>
<body>
<pre>{content}</pre>
</body>
</html>"""


def preview_html(lines: list) -> str:
    """生成预览用的 HTML（嵌入 Gradio）"""
    content = "\n".join(lines)
    return f"""<div class="preview-container"><pre>{content}</pre></div>"""


# ============ Gradio 回调函数 ============

def on_template_change(template_id: str):
    """模板改变时更新 glyph 下拉"""
    choices = get_glyph_choices(template_id)
    default_value = choices[0][1] if choices else "default"
    return gr.Dropdown(choices=choices, value=default_value)


def do_preview(img, template_id: str, glyph_id: str, width: int):
    """预览"""
    if img is None:
        return "<div style='background:#1e1e1e;padding:40px;border-radius:8px;color:#888;text-align:center;min-height:400px;display:flex;align-items:center;justify-content:center;'>请先上传图片</div>"

    try:
        img = limit_image_size(img)
        template = config.get_template(template_id)
        if not template:
            return "<p style='color:red'>无效的模板</p>"

        family_id = template.get("glyph_family", "")
        glyph_variant = config.get_glyph_variant(family_id, glyph_id) if glyph_id != "default" else config.get_glyph_variant(family_id)

        # 使用用户设置的宽度进行预览
        preview_w = min(width, PREVIEW_WIDTH)
        html_lines, _ = render_to_html_lines(img, template, glyph_variant, preview_w)
        return preview_html(html_lines)

    except Exception as e:
        return f"<p style='color:red'>预览失败: {str(e)}</p>"


def do_export_png(img, template_id: str, glyph_id: str, width: int):
    """导出 PNG - 渲染字符画为图像"""
    if img is None:
        gr.Warning("请先上传图片")
        return None

    try:
        img = limit_image_size(img)
        template = config.get_template(template_id)
        if not template:
            gr.Warning("无效的模板")
            return None

        width = min(width, MAX_WIDTH)
        family_id = template.get("glyph_family", "")
        glyph_variant = config.get_glyph_variant(family_id, glyph_id) if glyph_id != "default" else config.get_glyph_variant(family_id)

        # 渲染字符数据
        _, char_data = render_to_html_lines(img, template, glyph_variant, width)

        # 保存到临时文件
        timestamp = int(time.time())
        filename = f"terminal_art_{template_id}_{glyph_id}_{timestamp}.png"
        filepath = Path(tempfile.gettempdir()) / filename

        render_char_to_png(char_data, str(filepath))
        return str(filepath)

    except Exception as e:
        gr.Warning(f"导出失败: {str(e)}")
        return None


def do_export_html(img, template_id: str, glyph_id: str, width: int):
    """导出 HTML"""
    if img is None:
        gr.Warning("请先上传图片")
        return None

    try:
        img = limit_image_size(img)
        template = config.get_template(template_id)
        if not template:
            gr.Warning("无效的模板")
            return None

        width = min(width, MAX_WIDTH)
        family_id = template.get("glyph_family", "")
        glyph_variant = config.get_glyph_variant(family_id, glyph_id) if glyph_id != "default" else config.get_glyph_variant(family_id)

        html_lines, _ = render_to_html_lines(img, template, glyph_variant, width)
        html_content = wrap_html(html_lines, title=f"Terminal Art - {template_id}")

        timestamp = int(time.time())
        filename = f"terminal_art_{template_id}_{glyph_id}_{timestamp}.html"
        filepath = Path(tempfile.gettempdir()) / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(filepath)

    except Exception as e:
        gr.Warning(f"导出失败: {str(e)}")
        return None


# ============ Gradio 界面 ============

css = """
.preview-container {
    background: #1e1e1e;
    border-radius: 8px;
    padding: 10px;
    overflow: auto;
    min-height: 500px;
}
.preview-container pre {
    font-family: Consolas, Monaco, 'Courier New', monospace;
    font-size: 8px;
    line-height: 1.0;
    margin: 0;
    white-space: pre;
}
@media (max-width: 768px) {
    .main-row {
        flex-direction: column !important;
    }
    .preview-container {
        min-height: 300px;
    }
    .preview-container pre {
        font-size: 6px;
    }
}
"""

with gr.Blocks(title="终端图像渲染器", css=css) as demo:
    gr.Markdown("# 🎨 终端图像渲染器")
    gr.Markdown("将图片转换为终端风格的彩色字符画")

    with gr.Row(elem_classes="main-row"):
        # 左侧控制面板
        with gr.Column(scale=2, min_width=350):
            img_input = gr.Image(type="pil", label="上传图片", height=280)

            template_dropdown = gr.Dropdown(
                choices=get_template_choices(),
                value=config.templates[0]["id"] if config.templates else None,
                label="渲染模板"
            )

            glyph_dropdown = gr.Dropdown(
                choices=get_glyph_choices(config.templates[0]["id"]) if config.templates else [],
                value="v1",
                label="Glyph 变体"
            )

            width_slider = gr.Slider(
                minimum=60, maximum=MAX_WIDTH, value=150, step=10,
                label="渲染宽度（字符数）"
            )

            preview_btn = gr.Button("👁 预览", variant="primary", size="lg")

            with gr.Row():
                export_png_btn = gr.Button("📷 导出 PNG", size="sm")
                export_html_btn = gr.Button("🌐 导出 HTML", size="sm")

            with gr.Row():
                png_download = gr.File(label="PNG", scale=1)
                html_download = gr.File(label="HTML", scale=1)

        # 右侧预览区
        with gr.Column(scale=3):
            preview_output = gr.HTML(
                value="<div class='preview-container' style='display:flex;align-items:center;justify-content:center;color:#666;font-size:16px;'>上传图片后点击「预览」按钮</div>",
                label="预览效果"
            )

    # 事件绑定
    template_dropdown.change(
        fn=on_template_change,
        inputs=[template_dropdown],
        outputs=[glyph_dropdown]
    )

    preview_btn.click(
        fn=do_preview,
        inputs=[img_input, template_dropdown, glyph_dropdown, width_slider],
        outputs=[preview_output]
    )

    export_png_btn.click(
        fn=do_export_png,
        inputs=[img_input, template_dropdown, glyph_dropdown, width_slider],
        outputs=[png_download]
    )

    export_html_btn.click(
        fn=do_export_html,
        inputs=[img_input, template_dropdown, glyph_dropdown, width_slider],
        outputs=[html_download]
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )
