"""像素画生成器 - Gradio Web 应用核心"""

import tempfile
import time
from pathlib import Path
from PIL import Image

import gradio as gr

from src.engine.renderer import Config, Renderer
from src.engine.preprocess import resize
from src.engine.modes import render_to_html_data
from src.engine.exporter import export_char_png

# 常量
MAX_WIDTH = 300
PREVIEW_WIDTH = 180


class PixelArtApp:
    """像素画生成器应用"""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "presets.json"
        self.config = Config(config_path)
        self.renderer = Renderer(self.config)
    
    def get_template_choices(self):
        """获取模板下拉选项"""
        return [(f"{t['name']} - {t['desc']}", t['id']) for t in self.config.templates]

    def get_glyph_choices(self, template_id: str):
        """根据模板获取 glyph 下拉选项"""
        template = self.config.get_template(template_id)
        if not template:
            return [("默认", "default")]

        family_id = template.get("glyph_family", "")
        family = self.config.get_glyph_family(family_id)
        if not family or not family.get("variants"):
            return [("默认", "default")]

        choices = []
        default_id = family.get("default", "v1")

        for v in family["variants"]:
            glyph = v.get("glyph", "")
            charset = v.get("charset", "")

            if glyph:
                label = f"{v['name']} {glyph * 8}"
            elif charset:
                label = f"{v['name']} [{charset[:8]}]"
            else:
                label = v['name']

            if v["id"] == default_id:
                label += " ★"

            choices.append((label, v["id"]))

        return choices

    @staticmethod
    def limit_image_size(img: Image.Image, max_size: int = 6000) -> Image.Image:
        """限制图片尺寸"""
        w, h = img.size
        if max(w, h) > max_size:
            ratio = max_size / max(w, h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        return img

    def render_to_html_lines(self, img: Image.Image, template: dict, 
                             glyph_variant: dict, width: int) -> tuple:
        """渲染图片为 HTML 行"""
        mode = template.get("mode", "pixel_raw")
        aspect = template.get("defaults", {}).get("aspect", 0.5)

        if mode == "half_hd":
            aspect = aspect * 2

        img = resize(img, width, aspect)

        glyph = glyph_variant.get("glyph", "█") if glyph_variant else "█"
        charset = glyph_variant.get("charset", "") if glyph_variant else ""
        invert = template.get("defaults", {}).get("invert", False)

        return render_to_html_data(img, mode, glyph, charset, invert)

    def on_template_change(self, template_id: str):
        """模板改变时更新 glyph 下拉"""
        choices = self.get_glyph_choices(template_id)
        default_value = choices[0][1] if choices else "default"
        return gr.Dropdown(choices=choices, value=default_value)

    def do_preview(self, img, template_id: str, glyph_id: str, width: int):
        """预览"""
        if img is None:
            return """<div class="preview-box empty">
                <div class="empty-hint">
                    <span class="icon">🖼️</span>
                    <p>上传图片开始创作</p>
                </div>
            </div>"""

        try:
            img = self.limit_image_size(img)
            template = self.config.get_template(template_id)
            if not template:
                return "<div class='preview-box error'>无效的模板</div>"

            family_id = template.get("glyph_family", "")
            glyph_variant = self.config.get_glyph_variant(family_id, glyph_id) if glyph_id != "default" else self.config.get_glyph_variant(family_id)

            preview_w = min(width, PREVIEW_WIDTH)
            html_lines, _ = self.render_to_html_lines(img, template, glyph_variant, preview_w)
            content = "\n".join(html_lines)
            return f"""<div class="preview-box"><pre>{content}</pre></div>"""

        except Exception as e:
            return f"<div class='preview-box error'>预览失败: {str(e)}</div>"

    def do_export_png(self, img, template_id: str, glyph_id: str, width: int):
        """导出字符画图像"""
        if img is None:
            gr.Warning("请先上传图片")
            return None

        try:
            img = self.limit_image_size(img)
            template = self.config.get_template(template_id)
            if not template:
                gr.Warning("无效的模板")
                return None

            width = min(width, MAX_WIDTH)
            family_id = template.get("glyph_family", "")
            glyph_variant = self.config.get_glyph_variant(family_id, glyph_id) if glyph_id != "default" else self.config.get_glyph_variant(family_id)

            _, char_data = self.render_to_html_lines(img, template, glyph_variant, width)

            timestamp = int(time.time())
            filename = f"pixel_art_{template_id}_{timestamp}.png"
            filepath = Path(tempfile.gettempdir()) / filename

            export_char_png(char_data, str(filepath))
            return str(filepath)

        except Exception as e:
            gr.Warning(f"导出失败: {str(e)}")
            return None

    def do_export_html(self, img, template_id: str, glyph_id: str, width: int):
        """导出 HTML"""
        if img is None:
            gr.Warning("请先上传图片")
            return None

        try:
            img = self.limit_image_size(img)
            template = self.config.get_template(template_id)
            if not template:
                gr.Warning("无效的模板")
                return None

            width = min(width, MAX_WIDTH)
            family_id = template.get("glyph_family", "")
            glyph_variant = self.config.get_glyph_variant(family_id, glyph_id) if glyph_id != "default" else self.config.get_glyph_variant(family_id)

            html_lines, _ = self.render_to_html_lines(img, template, glyph_variant, width)
            content = "\n".join(html_lines)
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Pixel Art - {template_id}</title>
    <style>
        body {{ background-color: #1a1a2e; margin: 20px; }}
        pre {{ font-family: Consolas, Monaco, 'Courier New', monospace; font-size: 12px; line-height: 1.0; }}
    </style>
</head>
<body>
<pre>{content}</pre>
</body>
</html>"""

            timestamp = int(time.time())
            filename = f"pixel_art_{template_id}_{timestamp}.html"
            filepath = Path(tempfile.gettempdir()) / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            return str(filepath)

        except Exception as e:
            gr.Warning(f"导出失败: {str(e)}")
            return None


def get_css():
    """获取样式"""
    return """
/* 全局样式 */
.gradio-container {
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 20px !important;
}

/* 主布局强制横向 */
.main-row {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 20px;
}
.main-row > div:first-child {
    flex: 0 0 420px !important;
    max-width: 420px !important;
}
.main-row > div:last-child {
    flex: 1 1 auto !important;
}

/* 标题区域 */
.header-section {
    text-align: center;
    padding: 20px 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    margin-bottom: 20px;
}
.header-section h1 {
    color: white !important;
    font-size: 28px !important;
    margin: 0 !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}
.header-section p {
    color: rgba(255,255,255,0.9) !important;
    margin: 8px 0 0 0 !important;
    font-size: 14px !important;
}

/* 预览区域 */
.preview-panel { min-height: 500px; }
.preview-box {
    background: #1a1a2e;
    border-radius: 12px;
    padding: 16px;
    height: 480px;
    overflow: auto;
    display: flex;
    align-items: center;
    justify-content: center;
}
.preview-box pre {
    font-family: Consolas, Monaco, 'Courier New', monospace;
    font-size: 8px;
    line-height: 1.0;
    margin: 0;
    white-space: pre;
}
.preview-box.empty { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
.empty-hint { text-align: center; color: #666; }
.empty-hint .icon { font-size: 48px; display: block; margin-bottom: 12px; opacity: 0.5; }
.empty-hint p { margin: 0; font-size: 14px; }
.preview-box.error { color: #ff6b6b; font-size: 14px; }

/* 按钮样式 */
.primary-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    font-weight: 600 !important;
}
.export-btn { background: #f8f9fa !important; border: 1px solid #dee2e6 !important; }

/* 导出区域 */
.export-section { margin-top: 12px; }
.download-row { min-height: 50px; max-height: 50px; overflow: hidden; }

/* 手机竖屏布局 */
@media (max-width: 480px) {
    .gradio-container { padding: 10px !important; }
    .header-section h1 { font-size: 20px !important; }
    .main-row { flex-direction: column !important; }
    .main-row > div:first-child { max-width: 100% !important; }
    .preview-box { height: 260px; }
    .preview-box pre { font-size: 4px; }
}
"""


def create_app(config_path: Path = None) -> gr.Blocks:
    """创建 Gradio 应用"""
    app = PixelArtApp(config_path)
    
    with gr.Blocks(title="像素画生成器", css=get_css(), theme=gr.themes.Soft()) as demo:
        gr.HTML("""
            <div class="header-section">
                <h1>🎨 像素画生成器</h1>
                <p>上传图片，一键生成独特的像素风格艺术作品</p>
            </div>
        """)

        with gr.Row(equal_height=True, elem_classes="main-row"):
            with gr.Column(scale=1, min_width=280, elem_classes="control-panel"):
                img_input = gr.Image(type="pil", label="📷 上传图片", height=200, sources=["upload", "clipboard"])
                
                with gr.Group():
                    template_dropdown = gr.Dropdown(
                        choices=app.get_template_choices(),
                        value=app.config.templates[0]["id"] if app.config.templates else None,
                        label="🎭 渲染风格"
                    )
                    glyph_dropdown = gr.Dropdown(
                        choices=app.get_glyph_choices(app.config.templates[0]["id"]) if app.config.templates else [],
                        value="v1",
                        label="✨ 字符样式"
                    )
                    width_slider = gr.Slider(minimum=60, maximum=MAX_WIDTH, value=150, step=10, label="📐 精细度")
                
                preview_btn = gr.Button("🚀 生成预览", variant="primary", size="lg", elem_classes="primary-btn")
                
                with gr.Group(elem_classes="export-section"):
                    with gr.Row():
                        export_png_btn = gr.Button("💾 保存图片", size="sm", elem_classes="export-btn")
                        export_html_btn = gr.Button("🌐 保存网页", size="sm", elem_classes="export-btn")
                    with gr.Row(elem_classes="download-row"):
                        png_download = gr.File(label="图片", show_label=False, height=50)
                        html_download = gr.File(label="网页", show_label=False, height=50)

            with gr.Column(scale=2, min_width=300, elem_classes="preview-panel"):
                preview_output = gr.HTML(value="""<div class="preview-box empty">
                    <div class="empty-hint"><span class="icon">🖼️</span><p>上传图片开始创作</p></div>
                </div>""")

        # 事件绑定
        template_dropdown.change(fn=app.on_template_change, inputs=[template_dropdown], outputs=[glyph_dropdown])
        preview_btn.click(fn=app.do_preview, inputs=[img_input, template_dropdown, glyph_dropdown, width_slider], outputs=[preview_output])
        export_png_btn.click(fn=app.do_export_png, inputs=[img_input, template_dropdown, glyph_dropdown, width_slider], outputs=[png_download])
        export_html_btn.click(fn=app.do_export_html, inputs=[img_input, template_dropdown, glyph_dropdown, width_slider], outputs=[html_download])

    return demo
