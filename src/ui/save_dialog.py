"""保存对话框模块 - 支持 GUI 和命令行降级"""

_tk_available = True
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    _tk_available = False


def choose_save_path(ext: str, default_name: str = "output") -> str:
    """弹出保存对话框，返回用户选择的路径"""
    filetypes = {
        "png": ("PNG 图片", "*.png"),
        "html": ("HTML 文件", "*.html"),
        "ans": ("ANSI 文本", "*.ans"),
        "txt": ("文本文件", "*.txt"),
    }

    ft = filetypes.get(ext, ("所有文件", "*.*"))
    default_filename = f"{default_name}.{ext}"

    if _tk_available:
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)

            path = filedialog.asksaveasfilename(
                title="导出文件",
                initialfile=default_filename,
                defaultextension=f".{ext}",
                filetypes=[ft, ("所有文件", "*.*")]
            )

            root.destroy()
            return path if path else None
        except Exception:
            pass

    # 降级：命令行输入
    print(f"\n[提示] 无法打开文件对话框，请手动输入保存路径")
    print(f"默认文件名: {default_filename}")
    path = input("保存路径 (回车取消): ").strip()

    if not path:
        return None

    if not path.endswith(f".{ext}"):
        path = f"{path}.{ext}"

    return path
