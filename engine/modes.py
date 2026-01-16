"""渲染模式实现 - 各种渲染策略"""

from PIL import Image

from . import ansi
from .preprocess import brightness, mosaic, edge_detect, to_grayscale


def char_from_brightness(b: float, charset: str, invert: bool = False) -> str:
    """亮度映射到字符"""
    if invert:
        b = 1.0 - b
    idx = int(b * (len(charset) - 1))
    return charset[min(idx, len(charset) - 1)]


def render_pixel_raw(img: Image.Image, glyph: str = "█", delay: float = 0,
                     return_lines: bool = False):
    """像素映射 - 背景色块"""
    import time
    pixels = img.load()
    w, h = img.size
    lines = []

    for y in range(h):
        line = ""
        for x in range(w):
            r, g, b = pixels[x, y]
            line += ansi.bg(r, g, b) + " "
        line += ansi.reset()
        lines.append(line)
        if not return_lines:
            print(line, flush=True)
            if delay > 0:
                time.sleep(delay / 1000)

    return lines if return_lines else None


def render_pixel_mosaic(img: Image.Image, glyph: str = "█", delay: float = 0,
                        return_lines: bool = False):
    """马赛克映射 - 区域平均后的色块"""
    img = mosaic(img, 2)
    return render_pixel_raw(img, glyph, delay, return_lines)


def render_half_hd(img: Image.Image, glyph: str = "▀", delay: float = 0,
                   return_lines: bool = False):
    """半块映射 - 上下两像素合并"""
    import time
    pixels = img.load()
    w, h = img.size
    lines = []

    for y in range(0, h - 1, 2):
        line = ""
        for x in range(w):
            r1, g1, b1 = pixels[x, y]
            r2, g2, b2 = pixels[x, min(y + 1, h - 1)]
            if glyph == "▀":
                line += ansi.fg(r1, g1, b1) + ansi.bg(r2, g2, b2) + "▀"
            else:  # ▄
                line += ansi.fg(r2, g2, b2) + ansi.bg(r1, g1, b1) + "▄"
        line += ansi.reset()
        lines.append(line)
        if not return_lines:
            print(line, flush=True)
            if delay > 0:
                time.sleep(delay / 1000)

    return lines if return_lines else None


def render_char_luminance(img: Image.Image, charset: str = " .:-=+*#%@",
                          color_strategy: str = "truecolor_fg",
                          invert: bool = False, delay: float = 0,
                          return_lines: bool = False):
    """亮度字符 - 前景色+字符"""
    import time
    pixels = img.load()
    w, h = img.size
    lines = []

    for y in range(h):
        line = ""
        for x in range(w):
            r, g, b = pixels[x, y]
            br = brightness(r, g, b)
            char = char_from_brightness(br, charset, invert)
            if color_strategy == "truecolor_fg":
                line += ansi.fg(r, g, b) + char
            elif color_strategy == "grayscale":
                gray = int(br * 255)
                line += ansi.fg_gray(gray) + char
            else:  # mono
                line += char
        line += ansi.reset()
        lines.append(line)
        if not return_lines:
            print(line, flush=True)
            if delay > 0:
                time.sleep(delay / 1000)

    return lines if return_lines else None


def render_gray_level(img: Image.Image, charset: str = "░▒▓█",
                      invert: bool = False, delay: float = 0,
                      return_lines: bool = False):
    """灰度映射 - 灰度色+灰度字符"""
    import time
    img = to_grayscale(img)
    pixels = img.load()
    w, h = img.size
    lines = []

    for y in range(h):
        line = ""
        for x in range(w):
            r, g, b = pixels[x, y]
            br = brightness(r, g, b)
            char = char_from_brightness(br, charset, invert)
            gray = int(br * 255)
            line += ansi.fg_gray(gray) + char
        line += ansi.reset()
        lines.append(line)
        if not return_lines:
            print(line, flush=True)
            if delay > 0:
                time.sleep(delay / 1000)

    return lines if return_lines else None


def render_edge_structure(img: Image.Image, charset: str = "/\\|_-",
                          invert: bool = False, delay: float = 0,
                          return_lines: bool = False):
    """轮廓映射 - 边缘检测后的线稿"""
    import time
    img = edge_detect(img)
    pixels = img.load()
    w, h = img.size
    lines = []

    for y in range(h):
        line = ""
        for x in range(w):
            r, g, b = pixels[x, y]
            br = brightness(r, g, b)
            if invert:
                br = 1.0 - br
            if br > 0.1:
                idx = min(int(br * len(charset)), len(charset) - 1)
                line += charset[idx]
            else:
                line += " "
        lines.append(line)
        if not return_lines:
            print(line, flush=True)
            if delay > 0:
                time.sleep(delay / 1000)

    return lines if return_lines else None


# 模式注册表
MODE_REGISTRY = {
    "pixel_raw": render_pixel_raw,
    "pixel_mosaic": render_pixel_mosaic,
    "half_hd": render_half_hd,
    "char_luminance": render_char_luminance,
    "gray_level": render_gray_level,
    "edge_structure": render_edge_structure,
}
