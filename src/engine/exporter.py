"""导出模块 - PNG/HTML/ANSI 导出功能"""

import re
from PIL import Image, ImageDraw, ImageFont

CHAR_WIDTH = 8
CHAR_HEIGHT = 14


def export_png(img: Image.Image, path: str) -> bool:
    """导出采样后的原图为 PNG"""
    try:
        img.save(path, "PNG")
        return True
    except Exception as e:
        print(f"[ERR] PNG 导出失败: {e}")
        return False


def export_char_png(char_data: list, path: str) -> bool:
    """导出字符画为 PNG 图像"""
    if not char_data or not char_data[0]:
        print("[ERR] 无字符数据")
        return False

    try:
        rows = len(char_data)
        cols = len(char_data[0])

        img_width = cols * CHAR_WIDTH
        img_height = rows * CHAR_HEIGHT

        img = Image.new('RGB', (img_width, img_height), (30, 30, 30))
        draw = ImageDraw.Draw(img)

        font = None
        for font_name in ["consola.ttf", "DejaVuSansMono.ttf", "Courier New.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 12)
                break
            except:
                pass
        if font is None:
            font = ImageFont.load_default()

        for y, row in enumerate(char_data):
            for x, (char, r, g, b, bg_r, bg_g, bg_b) in enumerate(row):
                px = x * CHAR_WIDTH
                py = y * CHAR_HEIGHT
                draw.rectangle([px, py, px + CHAR_WIDTH, py + CHAR_HEIGHT],
                               fill=(bg_r, bg_g, bg_b))
                draw.text((px, py), char, fill=(r, g, b), font=font)

        img.save(path, "PNG")
        return True
    except Exception as e:
        print(f"[ERR] 字符画 PNG 导出失败: {e}")
        return False


def export_html(lines: list, path: str, title: str = "Pixel Art",
                font_family: str = "Consolas, Monaco, 'Courier New', monospace") -> bool:
    """导出为 HTML 文件"""
    try:
        html_lines = [ansi_to_html(line) for line in lines]

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ background-color: #1e1e1e; margin: 20px; }}
        pre {{ font-family: {font_family}; font-size: 12px; line-height: 1.0; }}
    </style>
</head>
<body>
<pre>{"".join(html_lines)}</pre>
</body>
</html>"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return True
    except Exception as e:
        print(f"[ERR] HTML 导出失败: {e}")
        return False


def ansi_to_html(line: str) -> str:
    """将 ANSI 转义序列转换为 HTML span"""
    ansi_pattern = re.compile(r'\x1b\[([0-9;]+)m')
    result = []
    fg_color = None
    bg_color = None
    pos = 0

    for match in ansi_pattern.finditer(line):
        if match.start() > pos:
            text = line[pos:match.start()]
            if text:
                style = _build_style(fg_color, bg_color)
                if style:
                    result.append(f'<span style="{style}">{_escape_html(text)}</span>')
                else:
                    result.append(_escape_html(text))

        codes = match.group(1).split(';')
        fg_color, bg_color = _parse_ansi_codes(codes, fg_color, bg_color)
        pos = match.end()

    if pos < len(line):
        text = line[pos:]
        if text:
            style = _build_style(fg_color, bg_color)
            if style:
                result.append(f'<span style="{style}">{_escape_html(text)}</span>')
            else:
                result.append(_escape_html(text))

    return "".join(result) + "\n"


def _parse_ansi_codes(codes: list, fg: str, bg: str) -> tuple:
    """解析 ANSI 颜色代码"""
    i = 0
    while i < len(codes):
        code = int(codes[i]) if codes[i].isdigit() else 0
        if code == 0:
            fg, bg = None, None
        elif code == 38 and i + 4 < len(codes) and codes[i + 1] == '2':
            r, g, b = codes[i + 2], codes[i + 3], codes[i + 4]
            fg = f"rgb({r},{g},{b})"
            i += 4
        elif code == 48 and i + 4 < len(codes) and codes[i + 1] == '2':
            r, g, b = codes[i + 2], codes[i + 3], codes[i + 4]
            bg = f"rgb({r},{g},{b})"
            i += 4
        i += 1
    return fg, bg


def _build_style(fg: str, bg: str) -> str:
    """构建 CSS 样式"""
    styles = []
    if fg:
        styles.append(f"color:{fg}")
    if bg:
        styles.append(f"background-color:{bg}")
    return ";".join(styles)


def _escape_html(text: str) -> str:
    """转义 HTML 特殊字符"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def export_ansi(lines: list, path: str) -> bool:
    """导出为 ANSI 文本文件"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("# ANSI Art File\n")
            f.write("# 播放: cat file.ans (Linux) / type file.ans (Windows)\n\n")
            for line in lines:
                f.write(line + "\n")
        return True
    except Exception as e:
        print(f"[ERR] ANSI 导出失败: {e}")
        return False
