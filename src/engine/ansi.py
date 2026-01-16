"""ANSI 终端工具模块 - 颜色输出、能力检测、降级处理"""

import io
import platform
import sys

# 强制 UTF-8 输出
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ansi_enabled = False
_truecolor_supported = True
_degraded_warned = False


def init():
    """初始化 ANSI 支持"""
    global _ansi_enabled
    if platform.system() == "Windows":
        try:
            import colorama
            colorama.init()
            _ansi_enabled = True
        except ImportError:
            try:
                import ctypes
                ctypes.windll.kernel32.SetConsoleMode(
                    ctypes.windll.kernel32.GetStdHandle(-11), 7
                )
                _ansi_enabled = True
            except Exception:
                pass
    else:
        _ansi_enabled = True


def fg(r: int, g: int, b: int) -> str:
    """24-bit 前景色"""
    return f"\x1b[38;2;{r};{g};{b}m"


def bg(r: int, g: int, b: int) -> str:
    """24-bit 背景色"""
    return f"\x1b[48;2;{r};{g};{b}m"


def fg_gray(level: int) -> str:
    """灰度前景色 (0-255)"""
    return f"\x1b[38;2;{level};{level};{level}m"


def bg_gray(level: int) -> str:
    """灰度背景色 (0-255)"""
    return f"\x1b[48;2;{level};{level};{level}m"


def reset() -> str:
    """重置颜色"""
    return "\x1b[0m"


def clear() -> str:
    """清屏"""
    return "\x1b[2J\x1b[H"


def clear_screen():
    """执行清屏"""
    print(clear(), end="", flush=True)


def check_truecolor() -> bool:
    """检测是否支持 TrueColor"""
    import os
    colorterm = os.environ.get("COLORTERM", "")
    return colorterm in ("truecolor", "24bit") or _truecolor_supported


def warn_degraded():
    """降级警告（只显示一次）"""
    global _degraded_warned
    if not _degraded_warned:
        print("[警告] 终端可能不支持 TrueColor，效果可能受限", flush=True)
        _degraded_warned = True


# 初始化
init()
