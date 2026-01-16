"""交互式界面 - 模板选择、glyph选择、预览、确认、导出"""

from engine.renderer import Renderer, Config
from engine.exporter import export_png, export_html, export_ansi
from .preview import render_preview
from .save_dialog import choose_save_path


def show_templates(config: Config) -> list:
    """显示模板列表"""
    templates = config.templates
    print("\n" + "=" * 50)
    print("  语义模板选择")
    print("=" * 50)
    for i, t in enumerate(templates, 1):
        print(f"  {i}) {t['name']} - {t['desc']}")
    print("  0) 退出")
    return templates


def show_glyphs(config: Config, family_id: str) -> list:
    """显示 glyph 变体列表（带可视化示例）"""
    family = config.get_glyph_family(family_id)
    if not family or not family.get("variants"):
        return []

    variants = family["variants"]
    default_id = family.get("default", "v1")

    print("\n  Glyph 变体选择:")
    print("  " + "-" * 46)
    for i, v in enumerate(variants, 1):
        default_mark = " (默认)" if v["id"] == default_id else ""
        glyph = v.get("glyph", "")
        charset = v.get("charset", "")

        if glyph:
            sample = glyph * 16
            print(f"  {i:2}) {v['name']:<6} '{glyph}' {sample} {v['desc']}{default_mark}")
        elif charset:
            display_charset = charset[:20] + "..." if len(charset) > 20 else charset
            print(f"  {i:2}) {v['name']:<6} [{display_charset}] {v['desc']}{default_mark}")

    print("  " + "-" * 46)
    print("  回车) 使用默认")
    return variants


def select_template(config: Config) -> dict:
    """选择模板"""
    templates = show_templates(config)
    choice = input("\n选择模板 [1-6]: ").strip()

    if choice == "0":
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(templates):
            return templates[idx]
    except ValueError:
        pass

    print("[提示] 无效选择，使用默认模板")
    return templates[0]


def select_glyph(config: Config, family_id: str) -> dict:
    """选择 glyph 变体"""
    if not family_id:
        return {}

    variants = show_glyphs(config, family_id)
    if not variants:
        return {}

    choice = input("  选择变体: ").strip()
    if not choice:
        return config.get_glyph_variant(family_id)

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(variants):
            return variants[idx]
    except ValueError:
        pass

    return config.get_glyph_variant(family_id)


def prompt_export(full_img, render_lines: list, template_id: str):
    """导出提示"""
    print("\n是否导出？")
    print("  1) 导出 PNG (采样图像)")
    print("  2) 导出 HTML (可浏览器查看)")
    print("  3) 导出 ANSI 文本 (终端回放)")
    print("  0) 不导出")

    choice = input("选择: ").strip()

    if choice == "1":
        path = choose_save_path("png", f"terminal_art_{template_id}")
        if path:
            if export_png(full_img, path):
                print(f"[OK] PNG 已保存: {path}")
            else:
                print("[ERR] PNG 导出失败")

    elif choice == "2":
        path = choose_save_path("html", f"terminal_art_{template_id}")
        if path:
            if export_html(render_lines, path, title=f"Terminal Art - {template_id}"):
                print(f"[OK] HTML 已保存: {path}")
            else:
                print("[ERR] HTML 导出失败")

    elif choice == "3":
        path = choose_save_path("ans", f"terminal_art_{template_id}")
        if path:
            if export_ansi(render_lines, path):
                print(f"[OK] ANSI 已保存: {path}")
            else:
                print("[ERR] ANSI 导出失败")


def interactive_session(renderer: Renderer, config: Config, default_image: str):
    """交互式会话"""
    print("\n" + "=" * 50)
    print("  终端图像渲染器")
    print("=" * 50)
    print(f"\n默认图片: {default_image}")
    path = input("图片路径 (回车=默认): ").strip() or default_image

    try:
        img = renderer.load_image(path)
        print(f"[OK] 图片加载成功: {img.size[0]}x{img.size[1]}")
    except FileNotFoundError:
        print(f"[ERR] 文件不存在: {path}")
        return
    except Exception as e:
        print(f"[ERR] 无法读取: {e}")
        return

    while True:
        template = select_template(config)
        if not template:
            return

        print(f"\n已选择: {template['name']}")

        family_id = template.get("glyph_family", "")
        glyph_variant = select_glyph(config, family_id)
        if glyph_variant:
            glyph_display = glyph_variant.get("glyph", "") or glyph_variant.get("charset", "")[:10]
            print(f"已选择 Glyph: {glyph_variant.get('name', 'default')} [{glyph_display}]")

        render_preview(img, template, glyph_variant, config, renderer)

        print("Enter) 渲染全图  B) 返回重选  0) 退出")
        action = input("选择: ").strip().lower()

        if action == "0":
            return
        elif action == "b":
            continue
        else:
            defaults = template.get("defaults", {})
            width = defaults.get("width", 150)
            aspect = defaults.get("aspect", 0.5)
            delay = defaults.get("delay", 0)
            invert = defaults.get("invert", False)
            do_clear = defaults.get("clear", False)

            mode = template.get("mode", "pixel_raw")
            full_img = renderer.prepare_image(img, width, aspect, mode)

            print(f"\n渲染中... (模式={template['id']}, 尺寸={full_img.size[0]}x{full_img.size[1]})")

            # 先渲染显示
            renderer.render(full_img, template, glyph_variant, delay, invert, do_clear)

            # 再获取渲染行（用于导出）
            render_lines = renderer.render(full_img, template, glyph_variant,
                                           delay=0, invert=invert, return_lines=True)

            glyph_id = glyph_variant.get("id", "default") if glyph_variant else "N/A"
            print(f"\n[完成] 模板={template['id']}, Glyph={glyph_id}, 尺寸={full_img.size[0]}x{full_img.size[1]}")

            # 导出提示
            prompt_export(full_img, render_lines, template['id'])
            return
