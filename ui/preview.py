"""预览模块 - 小尺寸预览渲染（使用前景色+字符确保可见）"""

from PIL import Image

from engine.preprocess import center_crop, resize, brightness
from engine import ansi


def render_preview(img: Image.Image, template: dict, glyph_variant: dict,
                   config, renderer):
    """渲染小预览 - 使用前景色+字符模式确保可见性"""
    defaults = config.defaults
    preview_w = defaults.get("preview_width", 40)
    preview_h = defaults.get("preview_height", 12)
    mode = template.get("mode", "pixel_raw")

    # 中心裁剪
    cropped = center_crop(img, preview_w, preview_h)

    # 缩放（half 模式需要双倍高度）
    aspect = 1.0 if mode == "half_hd" else 0.5
    preview_img = resize(cropped, preview_w, aspect)

    # 获取 glyph
    glyph = glyph_variant.get("glyph", "█") if glyph_variant else "█"
    charset = glyph_variant.get("charset", "") if glyph_variant else ""

    print("\n--- 预览 (前景色模式) ---")

    pixels = preview_img.load()
    w, h = preview_img.size

    if mode == "half_hd":
        # half 模式特殊处理
        half_glyph = glyph if glyph in ("▀", "▄") else "▀"
        for y in range(0, h - 1, 2):
            line = ""
            for x in range(w):
                r1, g1, b1 = pixels[x, y]
                r2, g2, b2 = pixels[x, min(y + 1, h - 1)]
                if half_glyph == "▀":
                    line += ansi.fg(r1, g1, b1) + ansi.bg(r2, g2, b2) + "▀"
                else:
                    line += ansi.fg(r2, g2, b2) + ansi.bg(r1, g1, b1) + "▄"
            print(line + ansi.reset(), flush=True)
    elif charset:
        # 字符集模式 - 使用前景色+字符
        for y in range(h):
            line = ""
            for x in range(w):
                r, g, b = pixels[x, y]
                br = brightness(r, g, b)
                idx = int(br * (len(charset) - 1))
                char = charset[min(idx, len(charset) - 1)]
                line += ansi.fg(r, g, b) + char
            print(line + ansi.reset(), flush=True)
    else:
        # 单字符模式 - 使用前景色+glyph（而非背景色+空格）
        for y in range(h):
            line = ""
            for x in range(w):
                r, g, b = pixels[x, y]
                line += ansi.fg(r, g, b) + glyph
            print(line + ansi.reset(), flush=True)

    print("--- 预览结束 ---\n")
