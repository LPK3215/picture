#!/usr/bin/env python3
"""
终端图像渲染器 - 程序入口

用法：
    # 交互式模式
    python main.py

    # 命令行模式 - 使用预设
    python main.py bg2.jpg --preset PIXEL_RAW
    python main.py bg2.jpg --preset HALF_HD --glyph v2 --width 180

    # 命令行模式 - 兼容旧参数
    python main.py bg2.jpg --mode bg --width 150
    python main.py bg2.jpg --mode half --width 180

参数：
    image              图片路径
    --preset, -p       预设模板 ID
    --glyph, -g        Glyph 变体 ID
    --mode, -m         兼容旧模式: fg/bg/half/mono
    --width, -w        输出宽度
    --aspect, -a       宽高比校正
    --delay, -d        每行延迟(ms)
    --invert, -i       反转亮度
    --clear            渲染前清屏
"""

import argparse
import sys

from engine.renderer import Renderer, Config
from ui.interactive import interactive_session

# 默认图片路径
DEFAULT_IMAGE = "data/bg2.jpg"


def run_cli(args, config: Config, renderer: Renderer):
    """命令行模式"""
    # 加载图片
    try:
        img = renderer.load_image(args.image)
    except FileNotFoundError:
        print(f"[ERR] 文件不存在: {args.image}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERR] 无法读取: {e}")
        sys.exit(1)

    # 确定模板
    template = None
    if args.preset:
        template = config.get_template(args.preset)
        if not template:
            print(f"[ERR] 未知预设: {args.preset}")
            print("可用预设:", [t["id"] for t in config.templates])
            sys.exit(1)
    elif args.mode:
        # 兼容旧模式
        preset_id = config.legacy_mapping.get(args.mode)
        if preset_id:
            template = config.get_template(preset_id)
        if not template:
            print(f"[ERR] 未知模式: {args.mode}")
            sys.exit(1)
    else:
        # 默认使用 PIXEL_RAW
        template = config.templates[0]

    # 获取 glyph
    family_id = template.get("glyph_family", "")
    glyph_variant = config.get_glyph_variant(family_id, args.glyph)

    # 合并参数（命令行 > 模板默认值）
    defaults = template.get("defaults", {})
    width = args.width if args.width else defaults.get("width", 150)
    aspect = args.aspect if args.aspect else defaults.get("aspect", 0.5)
    delay = args.delay if args.delay else defaults.get("delay", 0)
    invert = args.invert or defaults.get("invert", False)
    do_clear = args.clear or defaults.get("clear", False)

    # 准备图片
    mode = template.get("mode", "pixel_raw")
    full_img = renderer.prepare_image(img, width, aspect, mode)

    # 渲染
    print(f"渲染中... (预设={template['id']}, 尺寸={full_img.size[0]}x{full_img.size[1]})")
    renderer.render(full_img, template, glyph_variant, delay, invert, do_clear)

    glyph_id = glyph_variant.get("id", "default") if glyph_variant else "N/A"
    print(f"\n[完成] 预设={template['id']}, Glyph={glyph_id}, 尺寸={full_img.size[0]}x{full_img.size[1]}")


def main():
    config = Config()
    renderer = Renderer(config)

    # 无参数时进入交互模式
    if len(sys.argv) == 1:
        try:
            while True:
                interactive_session(renderer, config, DEFAULT_IMAGE)
                if input("\n继续? [Y/n]: ").strip().lower() == "n":
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n")
        return

    # 命令行模式
    parser = argparse.ArgumentParser(description="终端图像渲染器")
    parser.add_argument("image", help="图片路径")
    parser.add_argument("--preset", "-p", help="预设模板 ID")
    parser.add_argument("--glyph", "-g", help="Glyph 变体 ID")
    parser.add_argument("--mode", "-m", choices=["fg", "bg", "half", "mono"],
                        help="兼容旧模式")
    parser.add_argument("--width", "-w", type=int, help="输出宽度")
    parser.add_argument("--aspect", "-a", type=float, help="宽高比校正")
    parser.add_argument("--delay", "-d", type=float, help="每行延迟(ms)")
    parser.add_argument("--invert", "-i", action="store_true", help="反转亮度")
    parser.add_argument("--clear", action="store_true", help="渲染前清屏")

    args = parser.parse_args()
    run_cli(args, config, renderer)


if __name__ == "__main__":
    main()
