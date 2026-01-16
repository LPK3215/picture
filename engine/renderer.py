"""渲染引擎 - 图片加载、配置管理、渲染调度"""

import json
import shutil
from pathlib import Path

from PIL import Image

from . import ansi
from .modes import MODE_REGISTRY
from .preprocess import resize, center_crop


class Config:
    """配置管理器"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "presets.json"
        with open(config_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

    @property
    def defaults(self) -> dict:
        return self._data.get("defaults", {})

    @property
    def templates(self) -> list:
        return self._data.get("semantic_templates", [])

    @property
    def glyphs(self) -> dict:
        return self._data.get("glyph_variants", {})

    @property
    def legacy_mapping(self) -> dict:
        return self._data.get("legacy_mode_mapping", {})

    def get_template(self, template_id: str) -> dict:
        for t in self.templates:
            if t["id"] == template_id:
                return t
        return None

    def get_glyph_family(self, family_id: str) -> dict:
        return self.glyphs.get(family_id, {})

    def get_glyph_variant(self, family_id: str, variant_id: str = None) -> dict:
        family = self.get_glyph_family(family_id)
        if not family:
            return {}
        variants = family.get("variants", [])
        if not variant_id:
            variant_id = family.get("default", "v1")
        for v in variants:
            if v["id"] == variant_id:
                return v
        return variants[0] if variants else {}


class Renderer:
    """渲染引擎"""

    def __init__(self, config: Config = None):
        self.config = config or Config()

    def load_image(self, path: str) -> Image.Image:
        """加载图片"""
        return Image.open(path).convert("RGB")

    def get_terminal_width(self) -> int:
        """获取终端宽度"""
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80

    def prepare_image(self, img: Image.Image, width: int, aspect: float,
                      mode: str = None) -> Image.Image:
        """准备图片 - 缩放"""
        # half 模式需要双倍高度
        if mode == "half_hd":
            aspect = aspect * 2
        return resize(img, width, aspect)

    def prepare_preview(self, img: Image.Image, preview_width: int = 40,
                        preview_height: int = 12, mode: str = None) -> Image.Image:
        """准备预览图 - 中心裁剪+缩放"""
        cropped = center_crop(img, preview_width, preview_height)
        aspect = 1.0 if mode == "half_hd" else 0.5
        return resize(cropped, preview_width, aspect)

    def render(self, img: Image.Image, template: dict, glyph_variant: dict = None,
               delay: float = 0, invert: bool = False, clear: bool = False,
               return_lines: bool = False):
        """
        执行渲染

        Args:
            return_lines: 若为 True，则不打印，只返回渲染行列表（用于导出）
        """
        mode = template.get("mode", "pixel_raw")
        color_strategy = template.get("color_strategy", "truecolor")

        if clear and not return_lines:
            ansi.clear_screen()

        render_func = MODE_REGISTRY.get(mode)
        if not render_func:
            print(f"[错误] 未知渲染模式: {mode}")
            return None

        # 获取 glyph/charset
        glyph = "█"
        charset = " .:-=+*#%@"
        if glyph_variant:
            glyph = glyph_variant.get("glyph", glyph)
            charset = glyph_variant.get("charset", charset)

        # 根据模式调用不同参数
        if mode in ("pixel_raw", "pixel_mosaic"):
            return render_func(img, glyph=glyph, delay=delay, return_lines=return_lines)
        elif mode == "half_hd":
            return render_func(img, glyph=glyph, delay=delay, return_lines=return_lines)
        elif mode == "char_luminance":
            return render_func(img, charset=charset, color_strategy=color_strategy,
                               invert=invert, delay=delay, return_lines=return_lines)
        elif mode in ("gray_level", "edge_structure"):
            return render_func(img, charset=charset, invert=invert, delay=delay,
                               return_lines=return_lines)
        else:
            return render_func(img, delay=delay, return_lines=return_lines)
