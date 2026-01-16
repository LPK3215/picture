"""导出模块 - PNG/HTML/ANSI 导出功能"""

import re
from PIL import Image


def export_png(img: Image.Image, path: str) -> bool:
    """导出为 PNG 图片"""
    try:
        img.save(path, "PNG")
        return True
    except Exception as e:
        print(f"[ERR] PNG 导出失败: {e}")
        return False


def export_html(lines: list, path: str, title: str = "Terminal Art",
                font_family: str = "Consolas, Monaco, 'Courier New', monospace") -> bool:
    """
    导出为 HTML 文件

    Args:
        lines: 包含 ANSI 转义序列的行列表
        path: 保存路径
        title: HTML 标题
        font_family: 字体
    """
    try:
        html_lines = []
        for line in lines:
            html_line = ansi_to_html(line)
            html_lines.append(html_line)

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            background-color: #1e1e1e;
            margin: 20px;
        }}
        pre {{
            font-family: {font_family};
            font-size: 12px;
            line-height: 1.0;
            letter-spacing: 0;
        }}
        pre span {{
            display: inline;
        }}
    </style>
</head>
<body>
<pre>
{"".join(html_lines)}
</pre>
</body>
</html>
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return True
    except Exception as e:
        print(f"[ERR] HTML 导出失败: {e}")
        return False


def ansi_to_html(line: str) -> str:
    """将 ANSI 转义序列转换为 HTML span"""
    # 匹配 ANSI 转义序列
    ansi_pattern = re.compile(r'\x1b\[([0-9;]+)m')

    result = []
    fg_color = None
    bg_color = None
    pos = 0

    for match in ansi_pattern.finditer(line):
        # 添加匹配前的文本
        if match.start() > pos:
            text = line[pos:match.start()]
            if text:
                style = build_style(fg_color, bg_color)
                if style:
                    result.append(f'<span style="{style}">{escape_html(text)}</span>')
                else:
                    result.append(escape_html(text))

        # 解析 ANSI 代码
        codes = match.group(1).split(';')
        fg_color, bg_color = parse_ansi_codes(codes, fg_color, bg_color)
        pos = match.end()

    # 添加剩余文本
    if pos < len(line):
        text = line[pos:]
        if text:
            style = build_style(fg_color, bg_color)
            if style:
                result.append(f'<span style="{style}">{escape_html(text)}</span>')
            else:
                result.append(escape_html(text))

    return "".join(result) + "\n"


def parse_ansi_codes(codes: list, fg: str, bg: str) -> tuple:
    """解析 ANSI 颜色代码"""
    i = 0
    while i < len(codes):
        code = int(codes[i]) if codes[i].isdigit() else 0

        if code == 0:
            # Reset
            fg, bg = None, None
        elif code == 38 and i + 4 < len(codes) and codes[i + 1] == '2':
            # 24-bit 前景色: 38;2;R;G;B
            r, g, b = codes[i + 2], codes[i + 3], codes[i + 4]
            fg = f"rgb({r},{g},{b})"
            i += 4
        elif code == 48 and i + 4 < len(codes) and codes[i + 1] == '2':
            # 24-bit 背景色: 48;2;R;G;B
            r, g, b = codes[i + 2], codes[i + 3], codes[i + 4]
            bg = f"rgb({r},{g},{b})"
            i += 4

        i += 1

    return fg, bg


def build_style(fg: str, bg: str) -> str:
    """构建 CSS 样式"""
    styles = []
    if fg:
        styles.append(f"color:{fg}")
    if bg:
        styles.append(f"background-color:{bg}")
    return ";".join(styles)


def escape_html(text: str) -> str:
    """转义 HTML 特殊字符"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def export_ansi(lines: list, path: str) -> bool:
    """
    导出为 ANSI 文本文件

    Args:
        lines: 包含 ANSI 转义序列的行列表
        path: 保存路径
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            # 写入说明
            f.write("# ANSI Art File\n")
            f.write("# 播放方式: cat filename.ans (Linux/macOS)\n")
            f.write("# 或: type filename.ans (Windows Terminal)\n")
            f.write("# 或: less -R filename.ans\n")
            f.write("\n")
            # 写入内容
            for line in lines:
                f.write(line + "\n")
        return True
    except Exception as e:
        print(f"[ERR] ANSI 导出失败: {e}")
        return False
