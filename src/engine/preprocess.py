"""图像预处理模块 - 灰度、边缘检测、区域平均等"""

from PIL import Image, ImageFilter


def to_grayscale(img: Image.Image) -> Image.Image:
    """转换为灰度图"""
    return img.convert("L").convert("RGB")


def brightness(r: int, g: int, b: int) -> float:
    """计算亮度 (ITU-R BT.709)"""
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def resize(img: Image.Image, width: int, aspect: float) -> Image.Image:
    """按宽度等比缩放，aspect 用于补偿终端字符宽高比"""
    ratio = img.height / img.width
    height = max(1, int(width * ratio * aspect))
    return img.resize((width, height), Image.Resampling.LANCZOS)


def center_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """中心裁剪"""
    w, h = img.size
    crop_ratio = target_w / target_h
    img_ratio = w / h

    if img_ratio > crop_ratio:
        new_w = int(h * crop_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / crop_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    return img


def mosaic(img: Image.Image, block_size: int = 2) -> Image.Image:
    """马赛克效果 - 区域平均"""
    w, h = img.size
    small = img.resize((w // block_size, h // block_size), Image.Resampling.BOX)
    return small.resize((w, h), Image.Resampling.NEAREST)


def edge_detect(img: Image.Image) -> Image.Image:
    """边缘检测 (Sobel)"""
    gray = img.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    return edges.convert("RGB")


def invert_image(img: Image.Image) -> Image.Image:
    """反转图像"""
    from PIL import ImageOps
    return ImageOps.invert(img.convert("RGB"))
